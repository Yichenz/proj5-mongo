function create_memo() {
    
    var time = $('#time').val();
    var text = $('#text').val();
   
    $.ajax({
        'url': '/create_memo',
        'type': 'post',
        'data': {
            'time': time,
            'text': text,
        },
        'success': function(ret) {
            if (ret == 'ok') {
                // if create success, refresh the web
                window.location.reload();
            } else {
                // else report error message
                alert('create memo failed: ' + ret);
            }

        },
        'error': function(e) {
            // create failed
            alert('create memo failed: ' + e.statusText);
        }
    });
}

function remove_memo(id) {
    
    $.ajax({
        'url': '/remove_memo',
        'type': 'post',
        'data': {
            'id': id,
        },
        'success': function(ret) {
            if (ret == 'ok') {
                // if create success, refresh the web
                window.location.reload();
            } else {
                // else report error message
                alert('remove memo failed: ' + ret);
            }

        },
        'error': function(e) {
            // create failed
            alert('remove memo failed: ' + e.statusText);
        }
    });
}
