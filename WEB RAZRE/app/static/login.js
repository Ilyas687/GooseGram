$(document).ready(function(){
    $('#code_form').hide()
    $('#login_form').hide()
    $('.btn-53').click(function(){
        if (($('.input__search').val() != '') && ($('.input').val() != '')) (
            $.ajax({
                url: '/register/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({nickname: $('.input__search').val(), email: $('.email').val(), password: $('.input').val()}),
                success: function(response){
                    if (response.status == 'OK') {
                        $('.blue').hide()
                        $('#code_form').show()
                        $('#email2').val($('.email').val())
                    } else if (response.status == 'registered') {
                        alert('Пользователь с такой эл. почтой уже зарегистрирован')
                    }
                },
                error: function(xhr, status, error){
                    alert('Ошибка')
                }
            })
        )
    })
    $('.blue').click(function(){
        $('#login_form').slideToggle()
    })
})