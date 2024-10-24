function setQueryParam(key, value) {
  const url = new URL(window.location.href); // Get the current URL
  url.searchParams.set(key, value); // Set or update the query parameter
  window.history.pushState({}, "", url); // Update the URL without reloading the page
}

function getQueryParam(key) {
  const urlParams = new URLSearchParams(window.location.search); // Extract query params
  return urlParams.get(key); // Get the value of a specific query param
}

//    toaster function option

function loadtoasterOption() {
  toastr.options = {
    closeButton: true,
    debug: false,
    newestOnTop: false,
    progressBar: false,
    positionClass: "toast-bottom-right",
    preventDuplicates: false,
    onclick: null,
    showDuration: "300",
    hideDuration: "1000",
    timeOut: "5000",
    extendedTimeOut: "1000",
    showEasing: "swing",
    hideEasing: "linear",
    showMethod: "fadeIn",
    hideMethod: "fadeOut",
  };
}
