$(document).ready(function () {
  let timer = null;

  $("#txtOT").on("input", function () {
    clearTimeout(timer);
    let otId = $(this).val();
    let $input = $(this);

    if (!otId) {
      $input.removeClass("is-valid is-invalid");
      return;
    }

    timer = setTimeout(() => {
      $.ajax({
        url: `../api/ots/${otId}/`,
        type: "GET",
        success: function (response) {
          $input.removeClass("is-valid").addClass("is-invalid");
        },
        error: function (xhr) {
          if (xhr.status === 404) {
            $input.removeClass("is-invalid").addClass("is-valid");
          }
        },
      });
    }, 400);
  });
});

$("#txtTipoProyecto").select2({
  dropdownParent: $("#mdlCreate"),
});
