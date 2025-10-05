const LiveOutputComponent = {
    props: ['logs', 'isExecuting'],
    emits: ['clear'],
    template: `
        <div class="glass rounded-xl p-6 card">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-white">📊 Live Output</h3>
                <div class="flex items-center space-x-2">
                    <span v-if="isExecuting" class="text-green-400 text-sm animate-pulse-slow">
                        <i class="fas fa-spinner fa-spin mr-1"></i> Executing...
                    </span>
                    <button @click="$emit('clear')" class="btn bg-gray-500 hover:bg-gray-600 text-white py-1 px-3 rounded text-sm">
                        <i class="fas fa-trash mr-1"></i> Clear
                    </button>
                </div>
            </div>
            <div class="terminal rounded-lg p-4 h-96 overflow-y-auto" ref="terminal">
                <div v-for="log in logs" :key="log.id" 
                     class="log-entry text-sm"
                     :class="getLogClass(log.type)">
                    <span class="text-gray-400">{{ formatTime(log.timestamp) }}</span>
                    <span class="text-gray-300 ml-2">[{{ log.context }}]</span>
                    <span class="text-gray-100 ml-2">{{ log.message }}</span>
                </div>
                <div v-if="logs.length === 0" class="text-gray-500 text-center py-8">
                    No output yet. Run a command to see results.
                </div>
            </div>
        </div>
    `,
    methods: {
        getLogClass(type) {
            return 'log-' + type;
        },
        formatTime(timestamp) {
            return new Date(timestamp).toLocaleTimeString();
        }
    },
    updated() {
        this.$nextTick(() => {
            const terminal = this.$refs.terminal;
            if (terminal) {
                terminal.scrollTop = terminal.scrollHeight;
            }
        });
    }
};