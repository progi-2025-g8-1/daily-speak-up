<script setup>
    import { ref } from 'vue';
    import Dialog from 'primevue/dialog';
    import Button from 'primevue/button';
    import ToggleButton from 'primevue/togglebutton';
    import Textarea from 'primevue/textarea';
    import StarRating from './StarRating.vue';
    import { getUserId } from '../auth';

    const emits = defineEmits(['video-deleted']);

    const visible = ref(false);
    let dateString = ref('');
    const videoCaption = ref('');
    const videoVisibility = ref(false);
    const isOwner = ref(false);
    const averageRating = ref(null);
    const totalRatings = ref(0);
    const videoTopic = ref('');
    const videoInterest = ref('');

    const reportDialogVisible = ref(false);
    const reportReason = ref('');
    const reportLoading = ref(false);
    const reportError = ref('');

    let videoInfo = null;

    const checkIsOwner = async() => {
        try {
            const userId = await getUserId();
            isOwner.value = videoInfo && videoInfo.owner_id === userId;
        } catch (error) {
            console.error('Error fetching user ID:', error);
            isOwner.value = false;
        }
    }; 

    const handleVisibilitySwitch = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/video/${videoInfo.video_id}/visibility`, {
                method: 'PUT'
            });
            if (response.ok) {
                if (videoInfo.visibility === 'private') {
                    videoInfo.visibility = 'friends';
                } else {
                    videoInfo.visibility = 'private';
                }
            } else {
                console.error('Failed to toggle visibility');
                videoVisibility.value = !videoVisibility.value;
            }
        } catch (error) {
            console.error('Error toggling visibility:', error);
            videoVisibility.value = !videoVisibility.value;
        }
    };

    const deleteVideo = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/video/${videoInfo.video_id}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                visible.value = false;
                emits('video-deleted', videoInfo.video_id);
            } else {
                console.error('Failed to delete video');
            }
        } catch (error) {
            console.error('Error deleting video:', error);
        }
    };

    const handleRatingUpdated = (rating, newAverage, newTotal) => {
        averageRating.value = newAverage;
        totalRatings.value = newTotal;
    };

    const openReportDialog = () => {
        reportReason.value = '';
        reportError.value = '';
        reportDialogVisible.value = true;
    };

    const submitReport = async () => {
        if (!reportReason.value.trim()) {
            reportError.value = 'Please provide a reason';
            return;
        }

        reportLoading.value = true;
        reportError.value = '';

        try {
            const response = await fetch(
                `${import.meta.env.VITE_API_DOMAIN || window.ENV?.VITE_API_DOMAIN || 'http://localhost:8123'}/api/v1/speech/${videoInfo.video_id}/report`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ reason: reportReason.value })
                }
            );

            if (response.ok) {
                reportDialogVisible.value = false;
            } else if (response.status === 409) {
                reportError.value = 'You have already reported this speech';
            } else {
                reportError.value = 'Failed to submit report';
            }
        } catch (error) {
            console.error('Error submitting report:', error);
            reportError.value = 'Failed to submit report';
        } finally {
            reportLoading.value = false;
        }
    };

    const displaySpeechDialog = (date, hasSpeeches, video) => {
      if (hasSpeeches) {
        visible.value = true;
        dateString.value = `${date.getDate()}. ${date.getMonth() + 1}. ${date.getFullYear()}`;
        videoInfo = video;
        videoCaption.value = video.caption;
        videoVisibility.value = video.visibility === 'private';
        averageRating.value = video.average_rating;
        totalRatings.value = video.total_ratings || 0;
        videoTopic.value = video.topic || '';
        videoInterest.value = video.interest || '';
        checkIsOwner();
      }
    };

    defineExpose({
      displaySpeechDialog
    });
</script>


<template>
  <Dialog v-model:visible="visible" :draggable="false" modal class="w-[90vw] lg:w-[60vw] h-auto">
    <template #header>
        <div class="flex flex-col">
            <p class="text-xl lg:text-2xl font-semibold">{{ videoTopic || 'DailySpeakUp' }}</p>
            <p v-if="videoInterest" class="text-sm" style="color: var(--color-text-secondary);">{{ $t(`interests.${videoInterest}`) }} · {{ dateString }}</p>
            <p v-else class="text-sm" style="color: var(--color-text-secondary);">{{ dateString }}</p>
        </div>
    </template>
    <div class="w-full aspect-video flex flex-col items-center justify-center">
        <iframe 
            width="100%" 
            height="100%" 
            :src="videoInfo.url"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        ></iframe>
      </div>
      <div>{{ videoCaption }}</div>
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between w-full mt-6 gap-4">
          <StarRating
            v-if="videoInfo"
            :speech-id="videoInfo.video_id"
            :average-rating="averageRating"
            :total-ratings="totalRatings"
            @rating-updated="handleRatingUpdated"
          />
          <div class="flex flex-row items-center gap-2 lg:gap-4 w-full lg:w-auto">
            <div v-if="isOwner" class="flex flex-row items-center gap-2 lg:gap-4 flex-1 lg:flex-initial">
              <ToggleButton :onLabel="$t('speech.private')" :offLabel="$t('speech.friends')" onIcon="pi pi-lock"
                          offIcon="pi pi-lock-open" class="flex-1 lg:w-36" aria-label="Do you confirm"
                          @change="handleVisibilitySwitch" v-model="videoVisibility"/>
              <Button icon="pi pi-eraser" :label="$t('speech.delete')" severity="danger" v-on:click="deleteVideo" class="flex-1 lg:flex-initial" />
            </div>
            <div v-else class="w-full lg:w-auto">
              <Button icon="pi pi-flag" :label="$t('speech.report')" severity="warning" @click="openReportDialog" class="w-full lg:w-auto" />
            </div>
          </div>
      </div>

      <Dialog v-model:visible="reportDialogVisible" :header="$t('speech.report_dialog.title')" modal class="w-[90vw] lg:w-[30vw]">
          <div class="flex flex-col gap-4">
              <label for="report-reason">{{ $t('speech.report_dialog.reason_label') }}</label>
              <Textarea
                  id="report-reason"
                  v-model="reportReason"
                  :placeholder="$t('speech.report_dialog.reason_placeholder')"
                  rows="4"
                  class="w-full"
              />
              <small v-if="reportError" class="text-red-500">{{ reportError }}</small>
          </div>
          <template #footer>
              <Button :label="$t('speech.report_dialog.cancel')" severity="secondary" @click="reportDialogVisible = false" />
              <Button :label="$t('speech.report_dialog.submit')" severity="warning" @click="submitReport" :loading="reportLoading" />
          </template>
      </Dialog>
</Dialog>
</template>

<style scoped>
</style>