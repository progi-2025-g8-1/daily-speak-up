export interface DeleteVideoInstance {
  deleteVideo(videoId: string): void;
  refreshData?(): void;
  fetchVideos?(): Promise<void>;
}