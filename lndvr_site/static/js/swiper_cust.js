document.addEventListener("DOMContentLoaded", function () {
  new Swiper(".review-swiper", {
    loop: true,
    autoplay: {
      delay: 4000,
      disableOnInteraction: false,
    },
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
    spaceBetween: 30,
    slidesPerView: 1, // fallback default
    breakpoints: {
      640: { slidesPerView: 1 },
      768: { slidesPerView: 1 },
      1024: { slidesPerView: 3 },  // max 2 slides per view to avoid loop issues
    },
  });
});
