export function buildVideoConstraints() {
  return {
    width: 320,
    height: 320,
    aspectRatio: 1.0,
    frameRate: 30
  };
}

export function buildAudioConstraints() {
  return {
    sampleSize: 16,
    channelCount: 2,
    echoCancellation: false
  };
}