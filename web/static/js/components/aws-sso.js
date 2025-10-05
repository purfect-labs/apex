const AwsSsoComponent = {
    props: ['selectedEnv', 'isExecuting'],
    emits: ['sso-login', 'check-identity'],
    template: `
        <div class="glass rounded-xl p-6 card">
            <h3 class="text-lg font-semibold text-white mb-4">🔐 AWS SSO</h3>
            <div class="space-y-2">
                <button 
                    @click="$emit('sso-login')" 
                    :disabled="isExecuting"
                    class="w-full btn bg-blue-500 hover:bg-blue-600 text-white py-2 px-3 rounded-lg text-sm disabled:opacity-50">
                    <i class="fas fa-sign-in-alt mr-1"></i> SSO Login ({{ selectedEnv }})
                </button>
                <button 
                    @click="$emit('check-identity')" 
                    :disabled="isExecuting"
                    class="w-full btn bg-green-500 hover:bg-green-600 text-white py-2 px-3 rounded-lg text-sm disabled:opacity-50">
                    <i class="fas fa-user mr-1"></i> Check Identity
                </button>
            </div>
        </div>
    `
};