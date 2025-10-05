const PortForwardComponent = {
    props: ['services', 'portForwards'],
    emits: ['toggle-forward', 'open-browser'],
    template: `
        <div class="glass rounded-xl p-6 card">
            <h3 class="text-lg font-semibold text-white mb-4">🔗 Port Forwarding</h3>
            <div class="space-y-2">
                <div v-for="service in services" :key="service.name" class="flex items-center justify-between bg-black/20 rounded-lg p-3">
                    <div>
                        <span class="text-white font-medium">{{ service.name }}</span>
                        <span class="text-gray-300 text-sm block">:{{ service.port }}</span>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button 
                            @click="$emit('toggle-forward', service)" 
                            :class="isPortForwarded(service) ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'"
                            class="btn text-white py-1 px-3 rounded text-sm">
                            <i :class="isPortForwarded(service) ? 'fas fa-stop' : 'fas fa-play'" class="mr-1"></i>
                            {{ isPortForwarded(service) ? 'Stop' : 'Start' }}
                        </button>
                        <button 
                            v-if="isPortForwarded(service)" 
                            @click="$emit('open-browser', service)" 
                            class="btn bg-blue-500 hover:bg-blue-600 text-white py-1 px-3 rounded text-sm">
                            <i class="fas fa-external-link-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `,
    methods: {
        isPortForwarded(service) {
            return this.portForwards.includes(service.name + ':' + service.port);
        }
    }
};