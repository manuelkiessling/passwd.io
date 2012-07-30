var application = function() {
  
  var authformView = {
    init: function() {
      $('#load-button').click(function() {
        authformController.loadDossier();
      });
      $('#username, #passphrase').keypress(function(e) {
        if (e.which == 13) {
          authformController.loadDossier();
        }
      });
      $('#save-button').click(function() {
        authformController.saveDossier();
      });
    },
    getUsername: function() {
      return $('#username').val();
    },
    getPassphrase: function() {
      return $('#passphrase').val();
    },
    confirmShortPassphrase: function(message) {
      return confirm(message);
    },
    getContent: function() {
      return $('#dossier-content').val();
    },
    setContent: function(value) {
      $('#dossier-content').val(value);
    },
    showOverlay: function(cb) {
      $('#overlay').fadeIn('slow', cb);
    },
    hideOverlay: function(cb) {
      $('#overlay').fadeOut('slow', cb);
    },
  };

  var authformController = {
    _view: authformView,
    owner_hash: null,
    access_hash: null,
    init: function() {
      if (window.location.hash == '#editor' && this.owner_hash == null) {
        window.location.hash = '';
      }
    },
    loadDossier: function() {
      var my = this;
      var load = function() {
        if ( my._view.getUsername() && my._view.getPassphrase() ) {
          my.owner_hash = hash(my._view.getUsername(), '');
          my.access_hash = hash(my._view.getPassphrase(), my._view.getUsername());
          var url = '/api/dossier/load.json';
          var post_params = { 'owner_hash': my.owner_hash, 'access_hash': my.access_hash };
          var post = $.post(url, post_params);
  
          post.success(function(data) {
            $(data).each(function(index, value) {
              my._view.setContent(decrypt(value.content, my._view.getPassphrase()));
            });
            window.location.href = '#editor';
            my._view.hideOverlay(function() {});
          });
  
          post.error(function() {
            if (   my._view.getPassphrase().length > 15
                || my._view.confirmShortPassphrase('Please confirm that you want to use a passphrase that is less than 16 characters!')) {
              my.saveDossier(
                function() {
                  window.location.href = '#editor';
                },
                function() {
                  window.alert('Could neither load nor create - please try different credentials.');
                }
              );
              //window.alert('An error occured while trying to read from the server.');
            } else {
              my._view.hideOverlay(function() {});
            }
          });
        } else {
          window.alert('Please provide an eMail address and a passphrase.');
        }
      };
      this._view.showOverlay(load);
    },
    saveDossier: function(callbackOnSuccess, callbackOnError) {
      var my = this;
      if ( my._view.getUsername() && my._view.getPassphrase() ) {
        my._view.showOverlay(function() {
          var content = encrypt(my._view.getContent(), my._view.getPassphrase());
          var url = '/api/dossier/save.json';
          var post_params = { 'owner_hash': my.owner_hash, 'access_hash': my.access_hash, content: content };
          var post = $.post(url, post_params);
             
          post.success(function() {
            my._view.hideOverlay(function() {});
            if (callbackOnSuccess !== undefined) {
              callbackOnSuccess();
            } else {
              window.alert('Successfully stored your confidential data');
            }
          });
              
          post.error(function(error) {
            my._view.hideOverlay(function() {});
            if (callbackOnError !== undefined) {
              callbackOnError();
            } else {
              window.alert('An error occured while trying to write to the server.');
            }
          });
        });
      } else {
        window.alert('Please provide an eMail address and a passphrase.');
      }
    }
  };

  var hash = function(input, salt) {
    return sjcl.codec.hex.fromBits(sjcl.misc.pbkdf2(input, sjcl.codec.hex.fromBits(sjcl.hash.sha256.hash(salt)), 10000));
  };
  
  var encrypt = function(text, passphrase) {
    return sjcl.json.encrypt(passphrase, text);
  };

  var decrypt = function(encrypted, passphrase) {
    return sjcl.json.decrypt(passphrase, encrypted);
  };

  $('document').ready(function() {
    authformView.init();
    authformController.init();
    $('body').fadeIn();
  });

}();

