App = Em.Application.create();


App.VerificationCodeField = Em.TextField.extend();

App.UsernameField = Em.TextField.extend();

App.PasswordField = Em.TextField.extend({
    insertNewline: function() {
        App.editorController.loadDossier();
    }
});

App.ContentField = Em.TextArea.extend();

App.verificationController = Em.Object.create({
    token: '',
    verificationCode: '',
    captchaUrl: '',
    getToken: function() {
        var me = this;
        var url = '/getToken.json';
        var getJSON = $.getJSON(url, function(data) {
            $(data).each(function(index, value) {
                me.set('token', value.token);
            })
        });
        getJSON.success(function() {
            me.loadCaptcha();
        });
    },
    loadCaptcha: function() {
        var me = this;
        this.set('captchaUrl', '/getCaptcha.png?token=' + me.get('token'));
    },
    activateToken: function() {
        var me = this;
        var url = '/activateToken.json'
        var post = $.post(
            url,
            { 'token': me.get('token'), 'verification_code': me.get('verificationCode') }
        );
        post.success(function() {
          $('#captchaverification-layer').fadeOut(); 
        });
    }
});

App.verificationController.getToken();

App.editorController = Em.Object.create({
    username: '',
    password: '',
    content: '',
    statusLabelType: 'default',
    statusMessage: 'Ready.',
    loadDossier: function() {
        var me = this;
        if ( me.get("username") && me.get("password") ) {
            me.setLabelType('default');
            var owner_hash = sjcl.misc.pbkdf2(me.get("username"), "", 10000).toString();
            var access_hash = sjcl.misc.pbkdf2(me.get("password"), "", 10000).toString();
            var url = '/api/dossier/load.json'
                url += '?token=%@&owner_hash=%@&access_hash=%@'.fmt(App.verificationController.token, owner_hash, access_hash);
            var getJSON = $.getJSON(url, function(data) {
                $(data).each(function(index, value) {
                    me.set("content", sjcl.json.decrypt(me.get("password"), value.content));
                    me.setLabelType('success');
                    me.set('statusMessage', 'Successfully loaded dossier.');
                })
            });

            getJSON.error(function() {
                me.setLabelType('important');
                me.set('statusMessage', 'Error loading dossier.');
            });
        } else {
            me.setLabelType('warning');
            me.set('statusMessage', 'Please provide username and password.');
        }
    },
    saveDossier: function() {
        var me = this;
        if ( me.get("username") && me.get("password") ) {
            me.setLabelType('default');
            var owner_hash = sjcl.misc.pbkdf2(me.get("username"), "", 10000).toString();
            var access_hash = sjcl.misc.pbkdf2(me.get("password"), "", 10000).toString();
            var encrypted = sjcl.json.encrypt(me.get("password"), me.get("content"));
            var post = $.post(
                "/save.json?token=" + App.verificationController.token,
                { "owner_hash": owner_hash,
                  "access_hash": access_hash,
                  "content": encrypted }
            );
            
            post.success(function() {
                me.setLabelType('success');
                me.set('statusMessage', 'Successfully saved dossier.');
            });
            
            post.error(function(error) {
                me.setLabelType('important');
                me.set('statusMessage', 'Error saving dossier.');
            });
        }
    },
    setLabelType: function(type) {
        this.set('statusLabelType', 'label-' + type);
    }
});
