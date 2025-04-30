<script setup>
import { ref, computed } from 'vue'
import api from '@/services/api'

const taskLog = ref([])
const loading = ref(false)

const tasks = ref([])
const workers = ref([])

const newWorkerName = ref('')
const newWorkerSkill = ref('')
const newTaskDesc = ref('')
const newTaskLocation = ref('')

// Dropdown helpers
const workerDropdown = computed(() => workers.value.map(w => `${w.name} (${w.skills.join(', ')})`))
const taskDropdown = computed(() => tasks.value.map(t => `${t.description} (${t.location})`))

const addWorker = () => {
  if (!newWorkerName.value || !newWorkerSkill.value) return
  workers.value.push({
    name: newWorkerName.value,
    skills: [newWorkerSkill.value]
  })
  newWorkerName.value = ''
  newWorkerSkill.value = ''
}

const addTask = () => {
  if (!newTaskDesc.value || !newTaskLocation.value) return
  const nextId = tasks.value.length ? Math.max(...tasks.value.map(t => t.id)) + 1 : 1
  tasks.value.push({
    id: nextId,
    description: newTaskDesc.value,
    location: newTaskLocation.value
  })
  newTaskDesc.value = ''
  newTaskLocation.value = ''
}

const assignTasks = async () => {
  loading.value = true
  try {
    const res = await api.post(`/llm/assign_tasks`, {
      tasks: tasks.value,
      workers: workers.value
    })

    const assignment = res.data

    const tableData = Object.entries(assignment).flatMap(([worker, taskIds]) =>
      taskIds.map(id => ({
        worker,
        task: tasks.value.find(t => t.id === id)?.description || `Task ID ${id}`
      }))
    )

    taskLog.value.push({
      timestamp: new Date().toLocaleString(),
      raw: assignment,
      table: tableData
    })

    // Clear after assignment
    tasks.value = []
    workers.value = []
  } catch (err) {
    console.error('Error assigning tasks:', err)
    alert('Failed to assign tasks. Check backend.')
  } finally {
    loading.value = false
  }
}
</script>


<template>
  <div class="container">
    <div class="header-content">
      <span class="title">Dashboard</span>
      <button class="assign-btn" @click="assignTasks" :disabled="loading">
        <span v-if="loading" class="loader"></span>
        <span v-else>Assign Tasks</span>
      </button>
    </div>
    
    <div class="form-inputs">

      <div class="dropdown-section">
        <div>
          <h3>Create New Worker</h3>
          <div class="form-section">     
            <input v-model="newWorkerName" placeholder="Worker Name" />
            <input v-model="newWorkerSkill" placeholder="Skill" />
            <button @click="addWorker">+</button>
          </div>
        </div>
        <select>
          <option v-for="(worker, i) in workerDropdown" :key="i">{{ worker }}</option>
        </select>
      </div>
      
      <div class="dropdown-section">
        <div>
          <h3>Create New Task</h3>
            <div class="form-section">
              <input v-model="newTaskDesc" placeholder="Task Description" />
              <input v-model="newTaskLocation" placeholder="Location" />
              <button @click="addTask">+</button>
            </div>
            <select>
              <option v-for="(task, i) in taskDropdown" :key="i">{{ task }}</option>
            </select>
          </div>
      </div>
    </div>

    <main class="main-content">
      <div v-if="taskLog.length === 0">
        <p>No assignments yet.</p>
      </div>

      <div v-for="(log, index) in taskLog" :key="index" class="log-entry">
        <h3>{{ log.timestamp }}</h3>
        <table>
          <thead>
            <tr>
              <th>Worker</th>
              <th>Assigned Task</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in log.table" :key="i">
              <td>{{ row.worker }}</td>
              <td>{{ row.task }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<style scoped>

.dropdown-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 2vh;
}

.dropdown-section select {
  padding: 0.4rem;
  border-radius: 4px;
  border: 1px solid #ccc;
  min-width: 33vw;
}


.form-inputs {
  display: flex;
  gap: 3rem;
}

.form-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-section input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.form-section button {
  font-size: 1.2rem;
  font-weight: bold;
  padding: 0.4rem 1rem;
  background-color: #4fd1c5;
  color: #1e1e2f;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}


.container {
  display: flex;
  flex-direction: column;
  height: 200vh;
  overflow: hidden;
  padding: 2rem;
  font-family: 'Segoe UI', sans-serif;
  background-color: #f0f2f5;
}

.header-content {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.title {
  font-size: 3rem;
  font-weight: bold;
}

.subtitle {
  font-size: 2rem;
  color: #555;
}

.assign-btn {
  align-self: flex-start;
  background-color: #4fd1c5;
  color: #1e1e2f;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s ease;
}

.assign-btn:hover {
  background-color: #3bc4b5;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: #fff;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  overflow-y: auto;
  flex: 1;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  padding: 10px;
  border: 1px solid #ccc;
  text-align: left;
}

.log-entry {
  margin-bottom: 2rem;
}

.assign-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: #4fd1c5;
  color: #1e1e2f;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s ease;
}

.assign-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loader {
  width: 16px;
  height: 16px;
  border: 3px solid #fff;
  border-top: 3px solid #1e1e2f;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

</style>
