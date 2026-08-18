// Field order mirrors _video-player.json: video, poster — each field is a direct
// child div of the block. The "classes" multiselect field is rendered as CSS
// classes on the block itself rather than as a child div.
function fieldLink(block, index) {
  return block.querySelector(`:scope > div:nth-child(${index}) a`);
}

function fieldPicture(block, index) {
  return block.querySelector(`:scope > div:nth-child(${index}) picture`);
}

export default function decorate(block) {
  const videoLink = fieldLink(block, 1);
  const posterPicture = fieldPicture(block, 2);

  const autoplay = block.classList.contains('autoplay');
  const loop = block.classList.contains('loop');
  const muted = block.classList.contains('muted') || autoplay;
  const controls = !block.classList.contains('hide-controls');

  block.replaceChildren();

  if (!videoLink) return;

  const video = document.createElement('video');
  video.src = videoLink.href;
  video.controls = controls;
  video.loop = loop;
  video.muted = muted;
  video.playsInline = true;
  video.preload = autoplay ? 'auto' : 'metadata';

  const posterImg = posterPicture?.querySelector('img');
  if (posterImg) video.poster = posterImg.src;

  if (autoplay) {
    // Autoplay only proceeds unprompted in browsers when the video is muted.
    video.autoplay = true;
  }

  block.append(video);
}
