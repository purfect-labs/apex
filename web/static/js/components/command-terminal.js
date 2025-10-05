const CommandTerminalComponent = {
    props: ['modelValue', 'isExecuting'],
    emits: ['update:modelValue', 'execute'],
    template: `
        <div class="glass rounded-xl p-6 card">
            <h3 class="text-lg font-semibold text-white mb-4">💻 Command Terminal</h3>
            <div class="flex space-x-2">
                <input 
                    :value="modelValue"
                    @input="$emit('update:modelValue', $event.target.value)"
                    @keyup.enter="$emit('execute')"
                    placeholder="Enter command..."
                    class="flex-1 bg-black/30 text-white rounded-lg p-3 border border-white/20 focus:border-blue-400 focus:outline-none font-mono">
                <button 
                    @click="$emit('execute')" 
                    :disabled="isExecuting"
                    class="btn bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg disabled:opacity-50">
                    <i class="fas fa-play mr-2"></i> Execute
                </button>
            </div>
        </div>
    `
};