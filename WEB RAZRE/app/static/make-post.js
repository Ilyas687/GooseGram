let what = 'upload'
let images_number = 0
$(document).ready(function(){
    $.ajax({
        url: '/post-check/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({action: $('.upload-button').text()}),
        success: function(response){
            if (response.status == 'upload') {
                what = 'upload'
            } else if (response.status == 'change') {
                $('.post-title').val(response.post.title)
                $('.post-text').val(response.post.text)

                let imgs = response.post.imgs
                imgs.forEach(function(filename) {
                    $('#preview-container').append(`
                        <div style="position:relative; display:inline-block;">
                        <img src="/static/uploads/${filename}" 
                            style="max-width:100px; max-height:100px; border:1px solid #ccc; border-radius:5px;">
                        <button style="position:absolute; top:-5px; right:-5px; border:none; background:#f00; color:#fff;
                                        border-radius:50%; cursor:pointer; width:20px; height:20px; padding:0;">✖️</button>
                        </div>
                    `)
                    images_number++
                })
                what = 'edit'
            } else if (response.status == 'None') {

            } else {
                alert(`Ошибка: ${response.error}`)
            }
        },
        error: function(xhr, status, error){
            alert('Ошибка')
        }
    })
    
    // $('#triggerFileInput').click(function() {
    //     $('#fileInput').click(); 
    // });


    // $('#fileInput').change(function() {
    //     if (this.files.length > 0) {
    //         // imgs.append(this.files[0].name)
    //         // console.log(this.files[0].name);
    //         $('#file-text').text(this.files[0].name)
    //     }
    // });

    var $dropArea = $('#drop-area');
    var $fileInput = $('#fileElem');
    var $previewContainer = $('#preview-container');

    // Подсветка при перетаскивании
    $dropArea.on('dragover', function(e) {
        e.preventDefault();
        $(this).css('border-color', 'green');
    });

    $dropArea.on('dragleave', function() {
        $(this).css('border-color', '#ccc');
    });

    // Drop файлов
    $dropArea.on('drop', function(e) {
        e.preventDefault();
        $(this).css('border-color', '#ccc');
        var files = e.originalEvent.dataTransfer.files;
        handleFiles(files);
    });

    // Клик по области открывает окно выбора
    $dropArea.on('click', function() {
        $fileInput.click();
    });

    $fileInput.on('change', function() {
        var files = this.files;
        handleFiles(files);
    });

    // Обработка файлов
    var selectedFiles = []; // массив выбранных файлов

    function handleFiles(files) {
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




    $('.upload-button').click(function(){
        // var fileInput = $('#fileInput')[0];
        // var file = fileInput.files[0];

        // if (!file) {
        //     alert('Выберите файл!');
        //     return;
        // }

        // var formData = new FormData();
        // formData.append('file', file);

        if (selectedFiles.length === 0 && images_number <= 0) {
            alert('Выберите хотя бы одно изображение!');
            return;
        }

        var formData = new FormData();

        // Добавляем все выбранные файлы
        for (var i = 0; i < selectedFiles.length; i++) {
            formData.append('images[]', selectedFiles[i]);
        }

        let title = $('.post-title').val()
        let text = $('.post-text').val()

        formData.append('post_text', text); 
        formData.append('post_title', title);
        formData.append('post_images_n', images_number);
        
        if (text != '' && title != '' && what == 'upload') {
            $.ajax({
                url: '/add-post/',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response){
                    if (response.status == 'OK') {
                        alert('Пост добавлен')
                    } else if (response.status == 'already_exists') {
                        alert('Пост с таким названием уже существует на вашем аккаунте')
                    } else {
                        console.log(response.status)
                    }
                },
                error: function(xhr, status, error){
                    alert('Ошибка')
                }
            })
        } else if (what == 'edit') {
            $.ajax({
                url: '/change-post/',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response){
                    if (response.status == 'OK') {
                        alert('Пост изменен')
                    } else if (response.status == 'already_exists') {
                        alert('Пост с таким названием уже существует на вашем аккаунте')
                    } else {
                        console.log(response.status)
                    }
                },
                error: function(xhr, status, error){
                    alert('Ошибка')
                }
            })
        } else {
            alert('Заполните недостающие поля!')
        }
    })
})