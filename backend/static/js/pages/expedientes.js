//Select2
$("#ot").select2({
  dropdownParent: $("#mdlAddExp"),
});

$(document).on("click", ".edit", function () {
  const id = $(this).closest("tr").attr("id");
  $("#frmEdit").attr("data-id", id);
  $.get(`../api/sunarp/${id}/`, function (data) {
    $('select[name="estado"]').val(data.estado);
    $('select[name="entidad"]').val(data.entidad);
    $('select[name="oficina"]').val(data.oficina);
    $('input[name="numero"]').val(data.numero);
    $('input[name="presentacion"]').val(data.presentacion ? moment(data.presentacion).format("YYYY-MM-DD") : "");
    $('input[name="reingreso"]').val(data.reingreso ? moment(data.reingreso).format("YYYY-MM-DD") : "");
    $('input[name="vencimiento"]').val(data.vencimiento ? moment(data.vencimiento).format("YYYY-MM-DD") : "");
    $("#tblPagos tbody").empty();
    data.pagos.forEach(function (pago) {
      $("#tblPagos tbody").append(`
                <tr>
                    <td>${pago.monto}</td>
                    <td>${moment(pago.fecha).format("DD/MM/YYYY")}</td>
                </tr>
            `);
    });
    $("#tblActos tbody").empty();
    data.actos.forEach(function (acto) {
      $("#tblActos tbody").append(`
                <tr>
                    <td>${acto.acto_registral}</td>
                </tr>
            `);
    });
    $("#mdlEdit").modal("show");
  });
});
