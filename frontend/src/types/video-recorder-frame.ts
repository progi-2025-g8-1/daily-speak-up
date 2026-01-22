export interface VideoRecorderFrameInstance {
  startRecording(): void;
  stopRecording(): void;
  uploadData(uploadMethod: string, uploadUrl: string, userId: string, videoPath: string): void;
  setSpeechTopic(interest:string, topic: string): void;
}
