const DatabaseComponent = {
    props: ['selectedCloud', 'selectedEnv'],
    emits: ['check-tunnel', 'start-tunnel', 'test-connection'],
    template: `
        <div class="glass rounded-xl p-6 card">
            <h3 class="text-lg font-semibold text-white mb-4">🗄️ Database Tunnel</h3>
            <div class="space-y-3">
                <button 
                    @click="$emit('check-tunnel')" 
                    class="w-full btn bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded-lg text-sm">
                    <i class="fas fa-search mr-1"></i> Check DB Tunnel (Port 15432)
                </button>
                <button 
                    @click="$emit('start-tunnel')" 
                    class="w-full btn bg-green-500 hover:bg-green-600 text-white py-2 px-3 rounded-lg text-sm">
                    <i class="fas fa-database mr-1"></i> Start DB Tunnel ({{ selectedCloud }}/{{ selectedEnv }})
                </button>
                <button 
                    @click="$emit('test-connection')" 
                    class="w-full btn bg-purple-500 hover:bg-purple-600 text-white py-2 px-3 rounded-lg text-sm">
                    <i class="fas fa-terminal mr-1"></i> Test PSQL Connection
                </button>
            </div>
        </div>
    `
};
