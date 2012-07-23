var application = function() {
  
  var authformView = {
    init: function() {
      $('#load-button').click(function() {
        authformController.loadDossier();
      });
      $('#save-button').click(function() {
        authformController.saveDossier();
      });
    },
    getVerificationCode: function() {
      return $('#verificationcode').val();
    },
    getUsername: function() {
      return $('#username').val();
    },
    getPassphrase: function() {
      return $('#passphrase').val();
    },
    getContent: function() {
      return $('#dossier-content').val();
    },
    setContent: function(value) {
      $('#dossier-content').val(value);
    },
    setCaptchaUrl: function(url) {
      $('#captcha-image').attr('src', url);
    }
  };

  var authformController = {
    _view: authformView,
    token: null,
    tokenIsVerified: false,
    username: null,
    passphrase: null,
    getToken: function() {
      var my = this;
      var url = '/api/token/get.json';
      var getJSON = $.getJSON(url, function(data) {
        $(data).each(function(index, value) {
          my.token = value.token;
        })
      });
      getJSON.success(function() {
        my.loadCaptcha();
      });
    },
    loadCaptcha: function() {
      this._view.setCaptchaUrl('/getCaptcha.png?token=' + this.token);
    },
    activateToken: function(callback) {
      var my = this;
      var post_params = { token: my.token, 'verification_code': my._view.getVerificationCode() };
      var url = '/api/token/activate.json'
      var post = $.post(url, post_params);
      post.success(function() {
        my.tokenIsVerified = true;
        callback();
      });
      post.error(function() {
        window.alert('The image code is not correct.');
      });
    },
    loadDossier: function() {
      var my = this;
      var load = function() {
        if ( my._view.getUsername() && my._view.getPassphrase() ) {
          var owner_hash = hash(my._view.getUsername());
          var access_hash = hash(my._view.getPassphrase());
          var url = '/api/dossier/load.json';
              url += '?token=' + my.token;
              url += '&owner_hash=' + owner_hash;
              url += '&access_hash=' + access_hash;
          var getJSON = $.getJSON(url, function(data) {
            $(data).each(function(index, value) {
              my._view.setContent(decrypt(value.content, my._view.getPassphrase()));
            });
          });
  
          getJSON.success(function() {
            window.location.href = '#two';
          });
  
          getJSON.error(function() {
            my.saveDossier(
              function() {
                window.location.href = '#two';
              },
              function() {
                window.alert('Could neither load nor create - please try different credentials.');
              }
            );
            //window.alert('An error occured while trying to read from the server.');
          });
        } else {
          window.alert('Please provide an eMail address and a passphrase.');
        }
      };
      if (my.tokenIsVerified) {
        load();
      } else {
        my.activateToken(load);
      }
    },
    saveDossier: function(callbackOnSuccess, callbackOnError) {
      var my = this;
      if ( my._view.getUsername() && my._view.getPassphrase() ) {
        var owner_hash = hash(my._view.getUsername());
        var access_hash = hash(my._view.getPassphrase());
        var content = encrypt(my._view.getContent(), my._view.getPassphrase());
        var url = '/api/dossier/save.json';
            url += '?token=' + my.token;
        var post_params = { 'owner_hash': owner_hash, 'access_hash': access_hash, content: content };
        var post = $.post(url, post_params);
             
        post.success(function() {
          if (callbackOnSuccess !== undefined) {
            callbackOnSuccess();
          }
        });
            
        post.error(function(error) {
          if (callbackOnError !== undefined) {
            callbackOnError();
          } else {
            window.alert('An error occured while trying to write to the server.');
          }
        });
      } else {
        window.alert('Please provide an eMail address and a passphrase.');
      }
    }
  };

  var hash = function(input) {
    return sjcl.misc.pbkdf2(input, '', 10000).toString();
  };
  
  var encrypt = function(text, passphrase) {
    return sjcl.json.encrypt(passphrase, text);
  };

  var decrypt = function(encrypted, passphrase) {
    return sjcl.json.decrypt(passphrase, encrypted);
  };

  $('document').ready(function() {
    authformView.init();
    authformController.getToken();
  });

}();




/**




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
            var url = '/load.json'
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
*/
