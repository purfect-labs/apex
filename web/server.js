const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const http = require('http');
const socketIo = require('socket.io');
const pty = require('node-pty');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3000;
const PROJECT_ROOT = path.join(__dirname, '..');
const yaml = require('js-yaml');

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// API Routes
app.get('/api/status', (req, res) => {
  const configExists = fs.existsSync(path.join(PROJECT_ROOT, 'config', 'apex.yaml'));
  const awsConfigExists = fs.existsSync(path.join(PROJECT_ROOT, 'config', 'aws.sso.config'));
  
  res.json({
    configReady: configExists && awsConfigExists,
    configPath: path.join(PROJECT_ROOT, 'config'),
    projectRoot: PROJECT_ROOT
  });
});

app.post('/api/run-sso-auth', (req, res) => {
  // SSO auth should be done on host side, not in container
  res.json({
    success: false,
    error: 'SSO authentication must be done on host before starting container',
    message: 'Please run: bin/aws-sso-auth.sh on your host machine first',
    hostCommand: 'bin/aws-sso-auth.sh'
  });
});

app.get('/api/config', (req, res) => {
  const { cloud = 'aws', env = 'dev' } = req.query;
  
  try {
    const configPath = path.join(PROJECT_ROOT, 'config', 'apex.yaml');
    const configContent = fs.readFileSync(configPath, 'utf8');
    const config = yaml.load(configContent);
    
    const envConfig = config[cloud] && config[cloud][env];
    if (!envConfig) {
      return res.status(404).json({ error: `Configuration not found for ${cloud}/${env}` });
    }
    
    res.json({
      cloud,
      env,
      db_host: envConfig.db_host,
      db_name: envConfig.db_name, 
      db_user: envConfig.db_user,
      db_port: envConfig.db_port || '5432'
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to read configuration: ' + error.message });
  }
});

app.get('/api/aws-status', (req, res) => {
  const { env = 'dev' } = req.query;
  
  // Check if AWS credentials are available
  const child = spawn('aws', ['sts', 'get-caller-identity', '--profile', env], {
    cwd: PROJECT_ROOT
  });

  let output = '';
  let errorOutput = '';

  child.stdout.on('data', (data) => {
    output += data.toString();
  });

  child.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });

  child.on('close', (code) => {
    res.json({
      authenticated: code === 0,
      profile: env,
      identity: code === 0 ? JSON.parse(output) : null,
      error: code !== 0 ? errorOutput : null
    });
  });
});

app.post('/api/run-db-connect', (req, res) => {
  const { cloud = 'aws', env = 'dev' } = req.body;
  
  const apexScript = path.join(PROJECT_ROOT, 'bin', 'apex');
  
  if (!fs.existsSync(apexScript)) {
    return res.status(404).json({ error: 'apex script not found' });
  }

  // Note: This will run in background for port forwarding
  const child = spawn('bash', [apexScript, '--cloud', cloud, '--env', env, 'db-connect'], {
    cwd: PROJECT_ROOT,
    detached: true,
    stdio: ['ignore', 'pipe', 'pipe']
  });

  let output = '';
  let errorOutput = '';

  child.stdout.on('data', (data) => {
    output += data.toString();
    console.log('DB Connect Output:', data.toString());
  });

  child.stderr.on('data', (data) => {
    errorOutput += data.toString();
    console.log('DB Connect Error:', data.toString());
  });

  // Don't wait for close since this runs in background
  setTimeout(() => {
    res.json({
      success: true,
      message: 'DB connection started in background',
      output: output,
      pid: child.pid
    });
  }, 2000);
});

// WebSocket for terminal
const terminals = {};

io.on('connection', (socket) => {
  console.log('Client connected for terminal');

  socket.on('create-terminal', () => {
    console.log('Creating terminal for socket:', socket.id);
    
    // Get host connection info
    const hostUser = process.env.HOST_USER || 'shawn_meredith';
    const hostHome = process.env.HOST_HOME || '/Users/shawn_meredith';
    
    try {
      // Method 1: Try SSH to host (most reliable if SSH keys are set up)
      // For now, let's use a simpler approach with mounted volumes and proper PATH
      
      const terminal = pty.spawn('bash', [], {
        name: 'xterm-color',
        cols: 80,
        rows: 30,
        cwd: '/host-home/code/github/apex',
        env: {
          ...process.env,
          TERM: 'xterm-256color',
          PATH: '/host-usr-local-bin:/host-homebrew/bin:/usr/local/bin:/usr/bin:/bin',
          HOME: '/host-home',
          SHELL: '/bin/bash',
          PS1: `${hostUser}@host:\\w\\$ `
        }
      });

      terminals[socket.id] = terminal;
      console.log('Terminal spawned successfully for socket:', socket.id);

      // Send terminal output to client
      terminal.on('data', (data) => {
        console.log('Terminal data:', data.toString());
        socket.emit('terminal-output', data);
      });

      terminal.on('exit', (code, signal) => {
        console.log(`Terminal exited with code ${code}, signal ${signal}`);
        delete terminals[socket.id];
        socket.emit('terminal-exit');
      });
      
      terminal.on('error', (err) => {
        console.error('Terminal error:', err);
        socket.emit('terminal-error', err.message);
      });

      // Write initial prompt to get things started
      setTimeout(() => {
        terminal.write('\r\n');
      }, 100);

      socket.emit('terminal-ready');
    } catch (error) {
      console.error('Failed to create terminal:', error);
      socket.emit('terminal-error', error.message);
    }
  });

  socket.on('terminal-input', (data) => {
    const terminal = terminals[socket.id];
    if (terminal) {
      terminal.write(data);
    }
  });

  socket.on('terminal-resize', ({ cols, rows }) => {
    const terminal = terminals[socket.id];
    if (terminal) {
      terminal.resize(cols, rows);
    }
  });

  socket.on('disconnect', () => {
    const terminal = terminals[socket.id];
    if (terminal) {
      terminal.destroy();
      delete terminals[socket.id];
    }
    console.log('Client disconnected');
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`🚀 APEX Web UI running on http://localhost:${PORT}`);
  console.log(`📁 Project root: ${PROJECT_ROOT}`);
});