$(document).ready(function () {

    $(".categoria-link").click(function () {

        var categoriaId = $(this).children(".categoriaId")[0].value;
        var categoriaName = $(this).children(".categoriaName")[0].value;

        $.ajax({
            url: "/catalog/" + categoriaId + "/items/JSON",
            success: function(data) {
                var quantidade = data.items != undefined ? data.items.length : 0;
                var html = "<div class='menu-item'>" +
                            "    <h2>" + categoriaName  + " Items (" + quantidade + " Items)</h2>" +
                            "    <a class='item-link' href='/catalog/" + categoriaId + "/items/add'>" +
                            "     <i class=\"fas fa-plus\"></i> Add Item" +
                            "    </a>" +
                            "</div>";

                if(quantidade > 0) {
                    html += "<div class='menu-item mt-4'><ul>";

                    for (i = 0; i < quantidade; i++) {
                        var item = data.items[i];

                        ///" + categoriaId + "
                        html += "<li class='item'><a class='item-link' href='/catalog/items/" + item.id + "'><i class=\"fas fa-arrow-right\"></i> "
                            + item.name
                            + "</a><span class='item-categoria'> (" + categoriaName + ")</span>"
                            + "</li>";
                    }

                    html += "</ul></div>";
                }

                $(".latest-items-container").hide();
                $("#v-pills-" + categoriaId).html(html);
            }
        });
    });

    $('a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
        if(e.relatedTarget != undefined) {
            $(e.relatedTarget).removeClass('active');
        }
        e.target // newly activated tab
    });
})

// function showItemDetails(item) {
//     $.ajax({
//         url: "/catalog/items/"+ item + "/JSON",
//         success: function(data) {
//             alert(data);
//         }
//     });
// }
