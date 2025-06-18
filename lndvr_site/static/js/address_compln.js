function initAutocomplete() {
    const input = document.getElementById('business_add');
    const autocomplete = new google.maps.places.Autocomplete(input);

    autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace();
      console.log('Selected place:', place);
    });
  }