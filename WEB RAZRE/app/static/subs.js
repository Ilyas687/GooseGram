let liked = []
$(document).ready(function(){
    $.ajax({
        url: '/show_liked_posts/',
        type: 'POST',
        contentType: 'application/json',
        success: function(response){
            if (response.status == 'OK') {
                console.log(response)
                $.each(response.posts, function(index, post_info){
                    let is_checked = ''
                    if (post_info.liked) {
                        is_checked = ' checked'
                    }
                    $('.posts').append(`
<div class="post">
    <div class="post-info-points">
        <div class="post-info">
            <img src="/static/favicon.png" alt="" width="50" height="50">
            <div class="info-without-img">
                <h2 class="nickname">${post_info.nickname}</h2>
                <p>опубликовано ${post_info.time} назад</p>
            </div>
        </div>
        <!-- Три точки -->
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
                    if (!liked.includes(post_info.email)){
                        liked.push(post_info.email)
                        $('.subs').append(`
                            <button class="author_button" data-label="${post_info.nickname}">
                                <img src="/static/favicon.png" alt="">
                                <p id="phone">${post_info.nickname}</p>
                            </button>
                        `)
                    }
                })
            } else {
                alert(`Ошибка: ${response.status}`)
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

    $('.subs').on('wheel', function (e) {
        if (this.scrollWidth > this.clientWidth) {
            this.scrollLeft += e.originalEvent.deltaY
            e.stopPropagation()
            return false
        }
    })
})