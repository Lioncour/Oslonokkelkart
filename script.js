const CATEGORY_MAP = {
  bibliotek: 'Bibliotek',
  minigjenbruksstasjon: 'Små gjenvinningsstasjoner',
  gjenbruksstasjon: 'Store gjenvinningsstasjoner',
  annet: 'Diverse annet',
  bydelslokaler: 'Bydelslokaler',
  utstyrsutln: 'Utstyrsutlån',
  skole: 'Skole',
  debug: 'Debug',
  arbeidsplass: 'Arbeidsplass',
  hjelpemidler: 'Hjelpemidler',
  'farligavfall-container': 'Miljøstasjon for farlig avfall',
  idrettsanlegg: 'Idrettsanlegg',
  barnehager: 'Barnehager',
  seniorsenter: 'Seniorsenter',
  radhuset: 'Rådhus',
};

let map;
let markers = [];
let allItems = [];
let startDate = null;
const TIMELINE_START_DATE = new Date('2019-01-01');

document.addEventListener('DOMContentLoaded', () => {
  loadData().catch((error) => console.error('Failed to load data', error));
});

function initMap() {
  map = L.map('map', {
    center: [59.9139, 10.7522],
    zoom: 12,
    zoomControl: true,
    attributionControl: false,
  });

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    subdomains: ['a', 'b', 'c'],
  }).addTo(map);
}

function initTimeline() {
  if (!allItems.length) return;

  const slider = document.getElementById('timeline-slider');
  if (!slider) return;

  const normalizedStart = normalizeDate(TIMELINE_START_DATE);
  startDate = normalizedStart;
  const today = normalizeDate(new Date());
  const totalDays = Math.max(
    0,
    Math.round((today.getTime() - startDate.getTime()) / 86400000)
  );

  slider.min = 0;
  slider.max = totalDays;
  slider.value = totalDays;

  // Update slider fill and bubble position
  function updateSliderVisuals() {
    const value = Number(slider.value);
    const min = Number(slider.min);
    const max = Number(slider.max);
    const percent = max > 0 ? ((value - min) / (max - min)) * 100 : 0;
    
    const bubble = document.getElementById('slider-value-bubble');
    const fill = document.getElementById('slider-fill');
    const indicator = document.getElementById('slider-indicator-line');
    const container = slider.closest('.slider-container');
    
    if (container) {
      const sliderWidth = slider.offsetWidth;
      const position = (percent / 100) * sliderWidth;
      
      // Update fill width
      if (fill) {
        fill.style.width = `${position}px`;
      }
      
      // Update bubble and indicator position
      if (bubble) {
        bubble.style.left = `${position}px`;
      }
      
      if (indicator) {
        indicator.style.left = `${position}px`;
      }
      
      // Update bubble text with date
      const selectedDate = dateFromSliderValue(value);
      if (bubble) {
        bubble.textContent = formatDateShort(selectedDate);
      }
    }
  }

  slider.addEventListener('input', () => {
    const selectedDate = dateFromSliderValue(Number(slider.value));
    updateDateDisplay(selectedDate);
    updateMapMarkers(selectedDate);
    updateSliderVisuals();
  });

  // Initial update
  updateSliderVisuals();
}

function normalizeDate(date) {
  const normalized = new Date(date);
  normalized.setHours(0, 0, 0, 0);
  return normalized;
}

function dateFromSliderValue(value) {
  if (!startDate) return new Date();
  const date = new Date(startDate);
  date.setDate(startDate.getDate() + value);
  return date;
}

function formatDate(date) {
  return date.toLocaleDateString('no-NO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function formatDateShort(date) {
  return date.toLocaleDateString('no-NO', {
    day: 'numeric',
    month: 'short',
  });
}

function updateDateDisplay(date) {
  const dateDisplay = document.getElementById('date-display');
  if (dateDisplay) {
    dateDisplay.textContent = formatDate(date);
  }
}

function updateStats(visibleCount, categoryCounts = {}) {
  const totalEl = document.getElementById('visible-summary-total');
  const visibleEl = document.getElementById('visible-summary-count');
  const bubble = document.getElementById('location-count');
  const categoriesEl = document.getElementById('category-counts');

  const total = allItems.length;

  if (totalEl) totalEl.textContent = total.toString();
  if (visibleEl) visibleEl.textContent = visibleCount.toString();
  if (bubble) bubble.textContent = visibleCount.toString();

  if (categoriesEl) {
    categoriesEl.innerHTML = '';
    const sorted = Object.entries(categoryCounts)
      .filter(([, count]) => count > 0)
      .sort((a, b) => {
        if (b[1] !== a[1]) return b[1] - a[1];
        return a[0].localeCompare(b[0]);
      });

    sorted.forEach(([category, count]) => {
      const item = document.createElement('div');
      item.className = 'category-count-item';
      item.textContent = `${category}: ${count}`;
      categoriesEl.appendChild(item);
    });
  }
}

function createMarkerIcon() {
  return L.divIcon({
    className: 'map-marker',
    html: '<div class="marker-pin"></div>',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15],
  });
}

function updateMapMarkers(selectedDate) {
  markers.forEach((marker) => marker.remove());
  markers = [];

  const normalizedSelected = normalizeDate(selectedDate);
  let visible = 0;
  const categoryCounts = {};

  allItems.forEach((item) => {
    if (normalizedSelected >= item.dateObj) {
      const marker = L.marker([item.lat, item.lng], {
        icon: createMarkerIcon(),
      }).addTo(map);

      const category = item.category || 'Ukjent kategori';
      marker.bindPopup(
        `<strong>${item.name}</strong><br>${category}<br><small>${formatDate(
          item.dateObj
        )}</small>`
      );
      markers.push(marker);
      visible += 1;

      categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    }
  });

  updateStats(visible, categoryCounts);
}

function buildFallbackDataset() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return [
    {
      name: 'Oslo Rådhus',
      lat: 59.91273,
      lng: 10.73361,
      dateObj: new Date(today.getTime() - 86400000 * 365),
      category: 'Rådhus',
    },
  ];
}

async function loadData() {
  const hasWindowData =
    typeof window !== 'undefined' &&
    Array.isArray(window.LOCATIONS_DATA) &&
    window.LOCATIONS_DATA.length > 0;

  const hasGlobalConst =
    typeof LOCATIONS_DATA !== 'undefined' &&
    Array.isArray(LOCATIONS_DATA) &&
    LOCATIONS_DATA.length > 0;

  const inputData = hasWindowData
    ? window.LOCATIONS_DATA
    : hasGlobalConst
      ? LOCATIONS_DATA
      : null;

  if (inputData) {
    allItems = inputData.map((item) => {
      const dateObj = new Date(item.date);
      if (Number.isNaN(dateObj.getTime())) {
        const fallback = new Date();
        fallback.setHours(0, 0, 0, 0);
        return {
          ...item,
          dateObj: fallback,
          category: item.category || 'Ukjent kategori',
        };
      }

      dateObj.setHours(0, 0, 0, 0);
      return {
        ...item,
        dateObj,
        category: item.category || 'Ukjent kategori',
      };
    });
  } else {
    console.warn('LOCATIONS_DATA missing, using fallback dataset');
    allItems = buildFallbackDataset();
  }

  initMap();
  initTimeline();

  const slider = document.getElementById('timeline-slider');
  const currentDate = dateFromSliderValue(Number(slider?.value || 0));
  updateDateDisplay(currentDate);
  updateMapMarkers(currentDate);
  
  // Update slider visuals after initial load
  if (slider) {
    setTimeout(() => {
      const value = Number(slider.value);
      const min = Number(slider.min);
      const max = Number(slider.max);
      const percent = max > 0 ? ((value - min) / (max - min)) * 100 : 0;
      
      const bubble = document.getElementById('slider-value-bubble');
      const fill = document.getElementById('slider-fill');
      const indicator = document.getElementById('slider-indicator-line');
      const container = slider.closest('.slider-container');
      
      if (container) {
        const sliderWidth = slider.offsetWidth;
        const position = (percent / 100) * sliderWidth;
        
        if (fill) {
          fill.style.width = `${position}px`;
        }
        
        if (bubble) {
          bubble.style.left = `${position}px`;
          bubble.textContent = formatDateShort(currentDate);
        }
        
        if (indicator) {
          indicator.style.left = `${position}px`;
        }
      }
    }, 100);
  }
}
