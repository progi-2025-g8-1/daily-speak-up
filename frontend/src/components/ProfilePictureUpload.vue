<script setup lang="ts">
import { ref, computed } from 'vue'
import { api } from '../api'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Avatar from 'primevue/avatar'
import { useToast } from 'primevue/usetoast'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const toast = useToast()

const props = defineProps<{
  currentPhotoUrl?: string | null
  showLabel?: boolean
  size?: 'small' | 'medium' | 'large'
}>()

const emit = defineEmits<{
  (e: 'uploaded', url: string): void
  (e: 'deleted'): void
}>()

const uploadDialogVisible = ref(false)
const cameraDialogVisible = ref(false)
const uploading = ref(false)
const capturing = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const mediaStream = ref<MediaStream | null>(null)
const capturedImage = ref<string | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const avatarSize = computed(() => {
  switch (props.size) {
    case 'small': return 'xlarge'
    case 'large': return 'xlarge'
    default: return 'xlarge'
  }
})

const avatarClass = computed(() => {
  switch (props.size) {
    case 'small': return 'w-24 h-24'
    case 'large': return 'w-40 h-40'
    default: return 'w-32 h-32'
  }
})

function openUploadDialog() {
  uploadDialogVisible.value = true
}

function openFileUpload() {
  fileInputRef.value?.click()
}

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // Validate file type
  if (!file.type.startsWith('image/')) {
    toast.add({
      severity: 'error',
      summary: t('profile_upload.error'),
      detail: t('profile_upload.invalid_file_type'),
      life: 3000
    })
    return
  }
  
  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    toast.add({
      severity: 'error',
      summary: t('profile_upload.error'),
      detail: t('profile_upload.file_too_large'),
      life: 3000
    })
    return
  }
  
  await uploadPhoto(file)
  uploadDialogVisible.value = false
}

async function openCamera() {
  cameraDialogVisible.value = true
  uploadDialogVisible.value = false
  
  try {
    capturing.value = true
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        width: { ideal: 1280 },
        height: { ideal: 720 }
      } 
    })
    mediaStream.value = stream
    
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      await videoRef.value.play()
    }
    capturing.value = false
  } catch (error) {
    console.error('Error accessing camera:', error)
    toast.add({
      severity: 'error',
      summary: t('profile_upload.error'),
      detail: t('profile_upload.camera_access_denied'),
      life: 3000
    })
    cameraDialogVisible.value = false
    capturing.value = false
  }
}

function capturePhoto() {
  if (!videoRef.value || !canvasRef.value) return
  
  const video = videoRef.value
  const canvas = canvasRef.value
  
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  ctx.drawImage(video, 0, 0)
  capturedImage.value = canvas.toDataURL('image/png')
}

function retakePhoto() {
  capturedImage.value = null
}

async function confirmCapture() {
  if (!capturedImage.value) return
  
  // Convert data URL to Blob
  const response = await fetch(capturedImage.value)
  const blob = await response.blob()
  const file = new File([blob], 'profile-photo.png', { type: 'image/png' })
  
  await uploadPhoto(file)
  closeCameraDialog()
}

function closeCameraDialog() {
  // Stop camera stream
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop())
    mediaStream.value = null
  }
  
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
  
  capturedImage.value = null
  cameraDialogVisible.value = false
}

async function uploadPhoto(file: File) {
  uploading.value = true
  
  try {
    // Get upload URL from backend
    const contentType = file.type
    const uploadData = await api(`/photo/upload-url?content_type=${encodeURIComponent(contentType)}`)
    
    // Upload directly to S3 using presigned URL
    const uploadResponse = await fetch(uploadData.upload_url, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': contentType
      }
    })
    
    if (!uploadResponse.ok) {
      throw new Error('Failed to upload photo to S3')
    }
    
    // Update user profile with new photo URL
    const photoKey = uploadData.key
    await api('/user/me', {
      method: 'PATCH',
      body: JSON.stringify({ 
        profile_picture_url: photoKey 
      })
    })
    
    toast.add({
      severity: 'success',
      summary: t('profile_upload.success'),
      detail: t('profile_upload.photo_uploaded'),
      life: 3000
    })
    
    emit('uploaded', photoKey)
    
  } catch (error) {
    console.error('Error uploading photo:', error)
    toast.add({
      severity: 'error',
      summary: t('profile_upload.error'),
      detail: t('profile_upload.upload_failed'),
      life: 3000
    })
  } finally {
    uploading.value = false
  }
}

async function deletePhoto() {
  try {
    uploading.value = true
    
    await api('/user/me', {
      method: 'PATCH',
      body: JSON.stringify({ 
        profile_picture_url: null 
      })
    })
    
    toast.add({
      severity: 'success',
      summary: t('profile_upload.success'),
      detail: t('profile_upload.photo_deleted'),
      life: 3000
    })
    
    emit('deleted')
    uploadDialogVisible.value = false
    
  } catch (error) {
    console.error('Error deleting photo:', error)
    toast.add({
      severity: 'error',
      summary: t('profile_upload.error'),
      detail: t('profile_upload.delete_failed'),
      life: 3000
    })
  } finally {
    uploading.value = false
  }
}

defineExpose({
  openUploadDialog
})
</script>

<template>
  <div class="flex flex-col items-center gap-4">
    <!-- Avatar with upload button -->
    <div class="relative">
      <Avatar 
        v-if="currentPhotoUrl"
        :image="currentPhotoUrl"
        :size="avatarSize"
        :class="avatarClass"
        shape="circle"
        class="border-4 border-primary-100"
      />
      <Avatar 
        v-else
        icon="pi pi-user"
        :size="avatarSize"
        :class="avatarClass"
        shape="circle"
        class="border-4 border-primary-100 bg-primary-50 text-primary"
      />
      
      <Button
        icon="pi pi-camera"
        rounded
        class="absolute bottom-0 right-0 shadow-lg"
        size="small"
        @click="openUploadDialog"
        :disabled="uploading"
      />
    </div>
    
    <label v-if="showLabel" class="text-sm text-secondary">
      {{ t('profile_upload.click_to_upload') }}
    </label>

    <!-- Upload options dialog -->
    <Dialog 
      v-model:visible="uploadDialogVisible" 
      :header="t('profile_upload.choose_option')"
      :modal="true"
      :closable="true"
      class="w-full max-w-md"
    >
      <div class="flex flex-col gap-3 p-4">
        <Button
          :label="t('profile_upload.take_photo')"
          icon="pi pi-camera"
          class="w-full"
          @click="openCamera"
          :disabled="uploading"
        />
        
        <Button
          :label="t('profile_upload.upload_from_device')"
          icon="pi pi-upload"
          class="w-full"
          outlined
          @click="openFileUpload"
          :disabled="uploading"
        />
        
        <Button
          v-if="currentPhotoUrl"
          :label="t('profile_upload.delete_photo')"
          icon="pi pi-trash"
          severity="danger"
          class="w-full"
          outlined
          @click="deletePhoto"
          :disabled="uploading"
          :loading="uploading"
        />
      </div>
    </Dialog>

    <!-- Camera dialog -->
    <Dialog 
      v-model:visible="cameraDialogVisible"
      :header="t('profile_upload.take_photo')"
      :modal="true"
      :closable="true"
      class="w-full max-w-2xl"
      @hide="closeCameraDialog"
    >
      <div class="flex flex-col items-center gap-4 p-4">
        <div v-if="capturing" class="flex items-center gap-2">
          <i class="pi pi-spin pi-spinner"></i>
          <span>{{ t('profile_upload.starting_camera') }}</span>
        </div>
        
        <div v-else-if="!capturedImage" class="w-full">
          <video 
            ref="videoRef"
            class="w-full rounded-lg shadow-lg"
            autoplay
            playsinline
          ></video>
          
          <div class="flex justify-center mt-4">
            <Button
              :label="t('profile_upload.capture')"
              icon="pi pi-camera"
              size="large"
              @click="capturePhoto"
            />
          </div>
        </div>
        
        <div v-else class="w-full">
          <img 
            :src="capturedImage"
            class="w-full rounded-lg shadow-lg"
            alt="Captured photo"
          />
          
          <div class="flex justify-center gap-3 mt-4">
            <Button
              :label="t('profile_upload.retake')"
              icon="pi pi-refresh"
              outlined
              @click="retakePhoto"
            />
            <Button
              :label="t('profile_upload.use_photo')"
              icon="pi pi-check"
              @click="confirmCapture"
              :loading="uploading"
            />
          </div>
        </div>
      </div>
    </Dialog>

    <!-- Hidden file input -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      class="hidden"
      @change="handleFileSelect"
    />
    
    <!-- Hidden canvas for photo capture -->
    <canvas ref="canvasRef" class="hidden"></canvas>
  </div>
</template>
