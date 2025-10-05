const EnvironmentSelector = {
    props: {
        cloud: String,
        env: String
    },
    emits: ['update:cloud', 'update:env'],
    template: `
        <div class="glass rounded-xl p-6 card">
            <h3 class="text-lg font-semibold text-white mb-4">🌍 Environment</h3>
            <div class="space-y-3">
                <div>
                    <label class="block text-sm text-gray-200 mb-1">Cloud Provider</label>
                    <select 
                        :value="cloud" 
                        @input="$emit('update:cloud', $event.target.value)"
                        class="w-full bg-black/30 text-white rounded-lg p-2 border border-white/20 focus:border-blue-400 focus:outline-none">
                        <option value="aws">☁️ AWS</option>
                        <option value="gcp">🌍 Google Cloud</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm text-gray-200 mb-1">Environment</label>
                    <select 
                        :value="env" 
                        @input="$emit('update:env', $event.target.value)"
                        class="w-full bg-black/30 text-white rounded-lg p-2 border border-white/20 focus:border-blue-400 focus:outline-none">
                        <option value="dev">🧪 Development</option>
                        <option value="stage">🚀 Staging</option>
                        <option value="prod">⚡ Production</option>
                    </select>
                </div>
            </div>
        </div>
    `
};