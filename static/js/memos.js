function create_memo() {
    // first get datetime and text from input
    var time = $('#time').val();
    var text = $('#text').val();
    // check time and text
    if (!time || !text) {
        alert("please input time and text");
        return
    }
    // use ajax to request the server
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
    // use ajax to request the server
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
