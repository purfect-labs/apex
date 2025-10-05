const PsqlContainerComponent = {
    props: ['isExecuting'],
    emits: ['start-container', 'stop-container', 'check-status'],
    template: `
        <div class="glass rounded-xl p-6 card">
            <h3 class="text-lg font-semibold text-white mb-4">🐳 PSQL Container</h3>
            <div class="space-y-2">
                <button 
                    @click="$emit('start-container')" 
                    :disabled="isExecuting"
                    class="w-full btn bg-green-500 hover:bg-green-600 text-white py-2 px-3 rounded-lg text-sm disabled:opacity-50">
                    <i class="fas fa-play mr-1"></i> Start Container
                </button>
                <button 
                    @click="$emit('stop-container')" 
                    :disabled="isExecuting"
                    class="w-full btn bg-red-500 hover:bg-red-600 text-white py-2 px-3 rounded-lg text-sm disabled:opacity-50">
                    <i class="fas fa-stop mr-1"></i> Stop Container
                </button>
                <button 
                    @click="$emit('check-status')" 
                    :disabled="isExecuting"
                    class="w-full btn bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded-lg text-sm disabled:opacity-50">
                    <i class="fas fa-search mr-1"></i> Check Status
                </button>
            </div>
        </div>
    `
};