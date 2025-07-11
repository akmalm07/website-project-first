const featuredVideoEl = document.getElementById("featured-video");
const featuredTitleEl = document.getElementById("featured-title");
const featuredDescriptionEl = document.getElementById("featured-description");
const videoSectionsEl = document.getElementById("video-sections");

let videoData = null;  // Will hold fetched data

// Fetch video data from backend API
async function fetchVideoData() {
  try {
    const userId = localStorage.getItem("userId");

    if (!userId) {
      throw new Error("Missing user ID or auth token");
    }

    const response = await fetch(`.../${userId}/get_all_vids`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": userId
      }
    });


    document.addEventListener('contextmenu', function (e) {
    e.preventDefault();
  });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Failed to load video data");
    }

    console.log("Video data successfully fetched");
    videoData = data;
    init();
  } catch (err) {
    console.error("Error fetching video data:", err);
  }
}

// Initialize featured video and text with the first video
function loadFeaturedVideo(video) {
  if (!video) return;

  featuredTitleEl.textContent = video.title || "Untitled";
  featuredDescriptionEl.textContent = video.description || "";
  featuredVideoEl.src = video.signedUrl;
  featuredVideoEl.poster = video.signedPosterUrl;
  featuredVideoEl.load();
}

function buildVideoRow(category) {
  const section = document.createElement("div");
  section.className = "video-category";

  const title = document.createElement("h2");
  title.textContent = category.title;
  section.appendChild(title);

  const row = document.createElement("div");
  row.className = "video-row";

  category.videos.forEach((video, index) => {
    const card = document.createElement("div");
    card.className = "video-card";

    const img = document.createElement("img");
    img.src = video.signedPosterUrl;
    img.alt = video.title || `Video ${index + 1}`;
    img.loading = "lazy";

    const label = document.createElement("p");
    label.textContent = video.title || `Untitled Video`;
    label.className = "video-info";

    card.appendChild(img);
    card.appendChild(label);
    row.appendChild(card);
  });

  section.appendChild(row);
  return section;
}

// Initialize website content
function init() {
  // Load the first video as featured
  loadFeaturedVideo(videoData.videos?.[0]);

  // Build video section and add to page
  const category = { title: "All Videos", videos: videoData.videos };
  const row = buildVideoRow(category);
  videoSectionsEl.appendChild(row);

  // Add click listeners to each .video-card AFTER they exist in DOM
  document.querySelectorAll('.video-card').forEach((card, index) => {
    card.addEventListener('click', () => {
      // Load clicked video into featured video
      const video = videoData.videos[index];
      if (!video) return;

      loadFeaturedVideo(video);

      // Request fullscreen on featured video
      if (featuredVideoEl.requestFullscreen) {
        featuredVideoEl.requestFullscreen();
      } else if (featuredVideoEl.webkitRequestFullscreen) {
        featuredVideoEl.webkitRequestFullscreen();
      } else if (featuredVideoEl.msRequestFullscreen) {
        featuredVideoEl.msRequestFullscreen();
      }

      // Play featured video
      featuredVideoEl.play();
    });
  });
}

// Pause video when exiting fullscreen
function onFullscreenChange() {
  const isFullscreen = document.fullscreenElement 
                   || document.webkitFullscreenElement 
                   || document.msFullscreenElement;
  if (!isFullscreen) {
    featuredVideoEl.pause();
  }
}

document.addEventListener('fullscreenchange', onFullscreenChange);
document.addEventListener('webkitfullscreenchange', onFullscreenChange);
document.addEventListener('MSFullscreenChange', onFullscreenChange);


const accountBtn = document.getElementById('accountBtn');
const accountMenu = document.getElementById('accountMenu');

accountBtn.addEventListener('click', () => {
  const isHidden = accountMenu.getAttribute('aria-hidden') === 'true';
  accountMenu.setAttribute('aria-hidden', isHidden ? 'false' : 'true');
});

document.addEventListener('click', (e) => {
  if (!accountBtn.contains(e.target) && !accountMenu.contains(e.target)) {
    accountMenu.setAttribute('aria-hidden', 'true');
  }
});

// Start fetching videos on page load
fetchVideoData();
