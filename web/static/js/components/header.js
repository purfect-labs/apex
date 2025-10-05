const HeaderComponent = {
    props: ['status'],
    emits: ['refresh-status'],
    template: `
        <div class="glass rounded-2xl p-6 mb-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <h1 class="text-3xl font-bold text-white">🛠️ APEX Command Center</h1>
                    <span class="text-sm text-gray-200">2025 Edition</span>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="flex items-center space-x-2">
                        <span class="status-indicator" :class="getStatusClass('aws')"></span>
                        <span class="text-white text-sm">AWS</span>
                    </div>
                    <div class="flex items-center space-x-2">
                        <span class="status-indicator" :class="getStatusClass('gcp')"></span>
                        <span class="text-white text-sm">GCP</span>
                    </div>
                    <div class="flex items-center space-x-2">
                        <span class="status-indicator" :class="getStatusClass('kubernetes')"></span>
                        <span class="text-white text-sm">K8s</span>
                    </div>
                    <button @click="$emit('refresh-status')" class="btn bg-white/20 text-white px-3 py-1 rounded text-sm hover:bg-white/30">
                        <i class="fas fa-refresh mr-1"></i> Refresh
                    </button>
                </div>
            </div>
        </div>
    `,
    methods: {
        getStatusClass(service) {
            const status = this.status[service]?.status;
            if (status === 'authenticated' || status === 'connected' || status === 'available') {
                return 'status-online';
            } else if (status === 'not_authenticated' || status === 'not_connected' || status === 'error') {
                return 'status-offline';
            }
            return 'status-unknown';
        }
    }
};