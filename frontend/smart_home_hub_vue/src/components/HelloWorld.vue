<script setup lang="ts">
defineProps<{
  msg: string
}>()
</script>
<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';

export default defineComponent({
  data() {
    return {
      networkData: null,
    };
  },
  mounted() {
    this.fetchNetworkData();
  },
  methods: {
    fetchNetworkData() {
      axios.get('http://127.0.0.1:8000//networking/basic')  // URL to your Django view
        .then(response => {
          this.networkData = response.data;
        })
        .catch(error => {
          console.error('There was an error!', error);
        });
    }
  }
});
</script>
<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {

  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>

<template>

  <div class="container">
      <!-- Only render the table if networkData is not null -->
      <table v-if="networkData" class="table table-respnsive table-striped">
        <thead>
          <tr>
            <th>Interface</th>
            <th>Status</th>
            <th>Packets Sent</th>
            <th>Packets Received</th>
            <th>MTU</th>
            <th>Flags</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(stats, net_interface) in networkData.network_stats" :key="interface">
            <td>{{ net_interface }}</td>
            <td>{{ stats[0] ? 'Up' : 'Down' }}</td>
            <td>{{ stats[1] }}</td>
            <td>{{ stats[2] }}</td>
            <td>{{ stats[3] }}</td>
            <td>{{ stats[4] }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Optionally, display a message or loader while data is being fetched -->
      <div v-else>
        Loading network data...
      </div>
    </div>
</template>

