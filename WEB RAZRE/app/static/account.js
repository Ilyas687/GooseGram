let posts_number = 0
let profile_img = '/static/favicon.png'
$(document).ready(function(){ 

    $.ajax({
        url: '/check_profile_img/',
        type: 'POST',
        contentType: 'application/json',
        success: function(response){
            if (response.status == 'OK') {
                if (response.profile_img != 'None') {
                    $('.account-img').attr('src', `/static/uploads/users_profile_images/${response.profile_img}`)
                    profile_img = `/static/uploads/users_profile_images/${response.profile_img}`
                }
            } else {
                console.log(response.status)
            }
        },
        error: function(xhr, status, error){
            alert('Ошибка')
        }
    })

    $.ajax({
        url: '/get_profile/',
        type: 'POST',
        contentType: 'application/json',
        success: function(response){
            if (response.status == 'OK') {
                console.log(response)
                user_info = response.user_info
                $('.account-nickname').text(user_info.nickname)
                posts_number = user_info.posts
                $('.account-posts').text(`Опубликовал ${posts_number} пост(-а, -ов)`)
                if (user_info.posts > 0) {
                    $('.postss').css('display', 'block')
                    $('.posts').css('display', 'block')
                    $.each(response.posts, function(index, post_info){
                        let is_checked = ''
                        if (post_info.liked) {
                            is_checked = ' checked'
                        }

//                         let imgs = ''
//                         $.each(post_info.imgs, function(indexx, img){
//                             if (indexx == 0) {
//                                 imgs += `<img src="/static/uploads/${img}">`
//                             } else {
//                                 imgs += `
// <img src="/static/uploads/${img}">`
//                             }
//                         })

                        $('.posts').append(`
<div class="post">
    <div class="post-info-points">
        <div class="post-info">
            <img src="${profile_img}" alt="" class="account-img" width="50" height="50">
            <div class="info-without-img">
                <h2 class="nickname">${post_info.nickname}</h2>
                <p>опубликовано ${post_info.time} назад</p>
            </div>
        </div>
        <div class="hm_buttons">
            <form action="/edit-post/" method="post">
                <input type="hidden" name="title" value="${post_info.title}">
                <input type="hidden" name="text" value="${post_info.text}">
                <button class="edit">Редактировать</button>
            </form>
            <p>/</p>
            <button class="delete" ttitle="${post_info.title}">Удалить</button>
        </div>
    </div>
    <h2>${post_info.title}</h2>
    <p class="post-text">${post_info.text}</p>
    <div class="gallery"></div>
    <div class="post-not-user-info">
        <div class="commentaries-and-likes">
            <div class="likes">
                <div class="heart-container" title="Like">
                    <input type="checkbox" class="checkbox" id="Give-It-An-Id"${is_checked} email="${post_info.email}" title="${post_info.title}">
                    <div class="svg-container">
                        <svg viewBox="0 0 24 24" class="svg-outline" xmlns="http://www.w3.org/2000/svg">
                            <path d="M17.5,1.917a6.4,6.4,0,0,0-5.5,3.3,6.4,6.4,0,0,0-5.5-3.3A6.8,6.8,0,0,0,0,8.967c0,4.547,4.786,9.513,8.8,12.88a4.974,4.974,0,0,0,6.4,0C19.214,18.48,24,13.514,24,8.967A6.8,6.8,0,0,0,17.5,1.917Zm-3.585,18.4a2.973,2.973,0,0,1-3.83,0C4.947,16.006,2,11.87,2,8.967a4.8,4.8,0,0,1,4.5-5.05A4.8,4.8,0,0,1,11,8.967a1,1,0,0,0,2,0,4.8,4.8,0,0,1,4.5-5.05A4.8,4.8,0,0,1,22,8.967C22,11.87,19.053,16.006,13.915,20.313Z">
                            </path>
                        </svg>
                        <svg viewBox="0 0 24 24" class="svg-filled" xmlns="http://www.w3.org/2000/svg">
                            <path d="M17.5,1.917a6.4,6.4,0,0,0-5.5,3.3,6.4,6.4,0,0,0-5.5-3.3A6.8,6.8,0,0,0,0,8.967c0,4.547,4.786,9.513,8.8,12.88a4.974,4.974,0,0,0,6.4,0C19.214,18.48,24,13.514,24,8.967A6.8,6.8,0,0,0,17.5,1.917Z">
                            </path>
                        </svg>
                    </div>
                </div>
                <p class="">${post_info.likes}</p>
            </div>
            <div class="comms">
                <p class="comm-symbol">💬</p>
                <p>${Object.keys(post_info.commentaries).length}</p>
            </div>
        </div>
        <p class="write-comment">Напишите комментарий...</p>
    </div>
</div>
                        `)
                    })
                }
            } else {
                console.log(response.status)
            }
        },
        error: function(xhr, status, error){
            alert('Ошибка')
        }
    })


    $(document).on('change', '.heart-container input[type="checkbox"]', function(){
        let p = $(this).closest('.heart-container').next('p')
        let title = $(this).attr('title')
        let email = $(this).attr('email')
        if ($(this).is(':checked')) {
            $.ajax({
                url: '/increase_likes/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({email: email, title: title, sign: '+'}),
                success: function(response){
                    if (response.status == 'OK') {
                        let current = Number(p.text())
                        p.text(current + 1)
                    } else {
                        console.log(response.status)
                    }
                },
                error: function(xhr, status, error){
                    alert('Ошибка')
                }
            })
        } else {
            $.ajax({
                url: '/increase_likes/',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({email: email, title: title, sign: '-'}),
                success: function(response){
                    if (response.status == 'OK') {
                        let current = Number(p.text())
                        p.text(current - 1)
                    } else {
                        console.log(response.status)
                    }
                },
                error: function(xhr, status, error){
                    alert('Ошибка')
                }
            })
        }
    })

    $(document).on('click', '.delete', function(){
        let delete_button = $(this)
        let title = delete_button.attr('ttitle')
        $.ajax({
            url: '/delete_post/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({title: title}),
            success: function(response){
                if (response.status == 'OK') {
                    delete_button.closest('.post').remove()
                    posts_number--
                    $('.account-posts').text(`Опубликовал(-а) ${posts_number} пост(-а, -ов)`)
                    if (posts_number == 0) {
                        $('.postss').css('display', 'none')
                    }
                } else {
                    console.log(response.status)
                }
            },
            error: function(xhr, status, error){
                alert('Ошибка')
            }
        })
    })

    $('#change_profile_img').on('click', function(){
        $('#change_profile_img_input').click()
    })

    let selectedFiles = []

    function handleFile(files) {
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            if (file.type.startsWith('image/')) {
                selectedFiles.push(file);
                (function(f, index){
                    var reader = new FileReader();
                    reader.onload = function(e) {
                        var $imgWrapper = $('<div style="position:relative; display:inline-block;"></div>');
                        var $img = $('<img>').attr('src', e.target.result).css({
                            'max-width':'100px','max-height':'100px','border':'1px solid #ccc','border-radius':'5px'
                        });
                        var $delBtn = $('<button>✖️</button>').css({
                            position:'absolute', top:'-5px', right:'-5px', border:'none', background:'#f00', color:'#fff',
                            borderRadius:'50%', cursor:'pointer', width:'20px', height:'20px', padding:'0'
                        }).on('click', function(e){
                            e.stopPropagation(); // Важно: останавливаем всплытие, чтобы div не реагировал на клик
                            $imgWrapper.remove();
                            selectedFiles.splice(index, 1);
                            images_number--
                        });

                        $imgWrapper.append($img).append($delBtn);
                        $('#preview-container').append($imgWrapper);
                    };
                    reader.readAsDataURL(f);
                })(file, selectedFiles.length-1);
            } else {
                alert('Файл "' + file.name + '" не является изображением!');
            }
        }
        // Очищаем input только после добавления новых файлов, чтобы можно было выбрать их снова
        $('#fileElem').val('');
    }
    

    $('#change_profile_img_input').on('change', function() {
        var file = this.files;
        handleFile(file)

        var formData = new FormData();
        for (var i = 0; i < selectedFiles.length; i++) {
            formData.append('images[]', selectedFiles[i]);
        }
        
        $.ajax({
            url: '/change_profile_img/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response){
                if (response.status == 'OK') {
                    $('.account-img').attr('src', `/static/uploads/users_profile_images/${response.filename}`)
                } else {
                    console.log(response.status)
                }
            },
            error: function(xhr, status, error){
                alert('Ошибка')
            }
        })
    });
})

// /static/uploads/users_profile_images/${post_info.email}.png