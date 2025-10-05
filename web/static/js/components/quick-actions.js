const QuickActionsComponent = {
    props: ['selectedCloud', 'selectedEnv'],
    emits: ['execute'],
    template: `
        <div class="glass rounded-xl p-6 card">
            <h3 class="text-lg font-semibold text-white mb-4">⚡ Quick Actions</h3>
            <div class="grid grid-cols-2 gap-2">
                <button 
                    @click="$emit('execute', 'kubectl get pods -A', 'kubernetes')" 
                    class="btn bg-green-500 hover:bg-green-600 text-white py-2 px-3 rounded-lg text-sm">
                    <i class="fas fa-cubes mr-1"></i> Get Pods
                </button>
                <button 
                    @click="$emit('execute', 'aws lambda list-functions --region us-east-1 --profile ' + selectedEnv, 'aws')" 
                    class="btn bg-purple-500 hover:bg-purple-600 text-white py-2 px-3 rounded-lg text-sm">
                    <i class="fas fa-bolt mr-1"></i> Lambdas
                </button>
                <button 
                    @click="$emit('execute', 'git status', 'git')" 
                    class="btn bg-orange-500 hover:bg-orange-600 text-white py-2 px-3 rounded-lg text-sm">
                    <i class="fab fa-git-alt mr-1"></i> Git Status
                </button>
                <button 
                    @click="$emit('execute', 'aws s3 ls --profile ' + selectedEnv, 'aws')" 
                    class="btn bg-cyan-500 hover:bg-cyan-600 text-white py-2 px-3 rounded-lg text-sm">
                    <i class="fas fa-cloud mr-1"></i> S3 Buckets
                </button>
            </div>
        </div>
    `
};