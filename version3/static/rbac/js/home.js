    $(".item-title").click(function () {
        if ($(this).next().hasClass('hides')){
            $(this).next().removeClass('hides')
        }else {
            $(this).next().addClass('hides')
        }
    })