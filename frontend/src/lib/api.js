import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
})

export const dataApi = {
  getVideos(params) {
    return apiClient.get('/data/videos', { params })
  },
  getImages(params) {
    return apiClient.get('/data/images', { params })
  },
  getOpticalSensors(params) {
    return apiClient.get('/data/optical-sensors', { params })
  },
  getEquipmentSensors(params) {
    return apiClient.get('/data/equipment-sensors', { params })
  },
  getMotors(params) {
    return apiClient.get('/data/motors', { params })
  },
  getPower(params) {
    return apiClient.get('/data/power', { params })
  },
}

export const dashboardApi = {
  getOverview(params) {
    return apiClient.get('/dashboard/overview', { params })
  },
}

export const anomalyApi = {
  getImageQuality(params) {
    return apiClient.get('/anomalies/image-quality', { params })
  },
  getEquipmentOperation(params) {
    return apiClient.get('/anomalies/equipment-operation', { params })
  },
  getIntegrated(params) {
    return apiClient.get('/anomalies/integrated', { params })
  },
}

export const cameraApi = {
  list() {
    return apiClient.get('/cameras')
  },
  create(payload) {
    return apiClient.post('/cameras', payload)
  },
  update(id, payload) {
    return apiClient.put(`/cameras/${id}`, payload)
  },
  remove(id) {
    return apiClient.delete(`/cameras/${id}`)
  },
}

export const ioMetaApi = {
  list() {
    return apiClient.get('/io-meta')
  },
  create(payload) {
    return apiClient.post('/io-meta', payload)
  },
  update(id, payload) {
    return apiClient.put(`/io-meta/${id}`, payload)
  },
  remove(id) {
    return apiClient.delete(`/io-meta/${id}`)
  },
}

export const opticalConfigApi = {
  list() {
    return apiClient.get('/optical-config')
  },
  create(payload) {
    return apiClient.post('/optical-config', payload)
  },
  update(id, payload) {
    return apiClient.put(`/optical-config/${id}`, payload)
  },
  remove(id) {
    return apiClient.delete(`/optical-config/${id}`)
  },
}

export const opticalApi = {
  getHistory(params) {
    return apiClient.get('/optical/history', { params })
  },
}
