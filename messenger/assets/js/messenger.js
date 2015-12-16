define('In_messenger', ['In', 'In_ws'], function(IN, In_ws) {
  "use strict";
  
(function ($) {
  //
  
  IN.messenger = {
    sessions : {},
    read_message_ids : [],
    read_message_ids_interval : null
  };
  
  IN.messenger.queueMarkRead = function(id) {
	
	IN.messenger.read_message_ids.push(id);
	
    if (IN.messenger.read_message_ids_interval) {
	  return;  // already in queue
	}
	
	IN.messenger.read_message_ids_interval = setTimeout(function() {
	  IN.messenger.read_message_ids_interval = null;
	  IN.WS.send({
	    'ws_action' : 'messenger_mark_read',
	    'ids' : IN.messenger.read_message_ids
	  });
	  IN.messenger.read_message_ids = [];
	  
	  setTimeout(function() {
	    IN.WS.send({
	      'ws_action' : 'messenger_notification_count',
	    });
	  }, 1000);
	  
	}, 3000);
  }
  
  IN.messenger.initSession = function(args) {
	args['ws_action'] = 'messenger_init_session';
    IN.WS.send(args);
  }
  
  /**
   * Message Session object
   */
  IN.messenger.Session = function (message) {
    // get room details
    this.room_id = message['room'].id;
    this.room_name = message['room'].name;
    this.room_type = message['room'].type;
    this.panel_id = 'chat-room-' + this.room_id;
    
    this.last_message_id = -1;
    this.first_message_id = -1;
    this.is_in_state_update = false;
    
    this.pending_messages = [];
    
    if ('to_nabar_id' in message) {
        this.to_nabar_id = message.to_nabar_id;
        // set room id to data
        $(".messenger-trigger[data-nabar_id='" + this.to_nabar_id + "']").data('room_id', this.room_id);
    }
    
  };
  
  IN.messenger.Session.prototype.focus = function() {
    var panel_id = '#' + this.panel_id;
    var chatRoom = $(panel_id);
    
    if ($(panel_id + '-wrapper').length != 0) { // in room wrapper
	  this.scroll();
	  return;
	}
    
    var parent_id = chatRoom.parent().attr('id');
    
    if (chatRoom.length == 0) {
      return;
    }
    if (chatRoom.hasClass('closed')) {
      chatRoom.appendTo($('#messenger-inline-chat-room-wrapper'));   
      chatRoom.removeClass('closed');
    }

    if (!chatRoom.hasClass('opened')) {
      $(panel_id + ' .messenger-inline-flyout-content').stop().slideDown('fast'); // show
      chatRoom.addClass('opened');
    }
    
    IN.messenger.arrangeChatRooms();
    
    if (parent_id != 'messenger-inline-chat-room-wrapper') { // still not shown
      $('#messenger-inline-chat-room-wrapper').children().filter(':last').appendTo($('#messenger-inline-chat-room-wrapper-hidden'));
      chatRoom.appendTo($('#messenger-inline-chat-room-wrapper'));
    }
    
    this.scroll();
    
    $(panel_id + ' .messenger-inline-text-area').focus();
    
  };
  
  
  IN.messenger.Session.prototype.post = function(message, prepend) {
      
    if (this.is_in_state_update) { // update later
      message._prepend = prepend;
      this.pending_messages.push(message);
      return;
    }
    
    if (!message.message) {
	  return;
	}
    
    var panel_id = '#' + this.panel_id;
    var message_id = message.message.id;
    if (this.last_message_id < message_id) { // update message id
      this.last_message_id = message_id;
    }
    if (this.first_message_id == -1 || this.first_message_id > message_id) {
	  this.first_message_id = message_id;
	}
    if ($('Message-' + message_id).length != 0) { // already added
      // update?
    } else {
	  var msg_dom = $(message.message.message);
	  if (message.message.nabar_id == IN.nabar.id) {
	    msg_dom.addClass('me');
	  }
	  
	  if (message.message.read_status == 1) { // new
	    IN.messenger.queueMarkRead(message_id);
	  }
	  
      if (prepend) {
        msg_dom.prependTo(panel_id + ' .chat-history-content'); //.addClass('i-animation-fade');         
      } else {
        msg_dom.appendTo(panel_id + ' .chat-history-content'); //.addClass('i-animation-fade');
      }
    }
    
    // show if closed
    if ($(panel_id).hasClass('closed')) {
      $(panel_id).appendTo($('#messenger-inline-chat-room-wrapper'));   
      $(panel_id).removeClass('closed');
    }
    
    this.scroll(prepend);
	
    /*
    .hide().fadeIn( 'normal', function() {});
    */
    
    IN.trigger('dom', true); // dom changed
    
  };
  
  IN.messenger.Session.prototype.scroll = function(top) {
	var cid = '#' + this.panel_id + ' .chat-history';
	if (top) {
	  $(cid).scrollTop(0);
	} else {
      $(cid).scrollTop($(cid)[0].scrollHeight);
    }
  };
  
  IN.on('In.ws.onopen', 'In.messenger', 'messenger', {
    bind : function() {
      setTimeout(function() {
		var rooms = {};
        for (var room_id in IN.messenger.sessions) {
          var session = IN.messenger.sessions[room_id];
          rooms[room_id] = session.last_message_id;
          session.is_in_state_update = true;
        }
        IN.WS.send({
          'ws_action' : 'messenger_rooms_state',
          'rooms_state' : rooms
        });
      }, 2000);
      
      /*setTimeout(function() {
        IN.WS.send({
          'ws_action' : 'messenger_notification_count',
        });
      }, 4000);*/
    }
  });
  
  IN.on('dom', 'In.messenger', 'messenger', {
    bind : function() {
      $('.messenger-trigger').once('messenger-trigger', function() {
        $(this).on('click', function(event) {
            var room_id = $(this).data('room_id');
            
            if (room_id) {
                if (room_id in IN.messenger.sessions) {
                  var session = IN.messenger.sessions[room_id];
                  session.focus();
                  return;
                } else {
				  IN.messenger.initSession({
                    room_id : room_id
                  });
                }
            } else {
                var nabar_id = $(this).data('nabar_id');
                if (nabar_id) {
                  IN.messenger.initSession({
                    to_nabar_id : nabar_id
                  });
                }
            }
        });
      });
      
      $('.messenger-load-more-messages').once('messenger-load-more', function() {
		  $(this).on('click', function(event) {
            var room_id = $(this).data('room_id');
            if (room_id && room_id in IN.messenger.sessions) {
			  var session = IN.messenger.sessions[room_id];
			  
			  IN.WS.send({
			    'ws_action' : 'messenger_room_messages_load_more',
			    room_id : room_id,
			    first_message_id : session.first_message_id
			  });
			}
          });
          if ($(this).hasClass('click-now')) {
			$(this).removeClass('click-now');
			$(this).click();
		  }
	  });
    }
  });
  
  /*
   * WS Messenger Commands 
   */
  IN.WSCommands.prototype.init_session = function(message) {
    
    var room_id = message['room'].id;
    
    // create session
    if (!(room_id in IN.messenger.sessions)) {
      var session = new IN.messenger.Session(message);
      IN.messenger.sessions[room_id] = session;
    } else {
      var session = IN.messenger.sessions[room_id]
    }
    
    var panel_id = 'chat-room-' + room_id;
    
    if ($('#' + panel_id).length != 0) {
	  if ($('#' + panel_id + '-wrapper').length != 0) {
	    var parent_id = $('#' + panel_id).parent().attr('id');
	    if (parent_id != panel_id + '-wrapper') {
		  $('#' + panel_id).appendTo('#' + panel_id + '-wrapper');
		}
	  }
      session.focus();
      return;  // already created
    }
    
    var room_name = message['room'].name;
    var room_type = message['room'].type;
    
    var online_status = 0;
    var opened = true;
    
    var chat_settings_id = 'messenger_inline_chat_room_settings_' + room_id;
    var chat_settings_form_id = 'messenger-inline-chat-room-settings-form-' + room_id;
    var messages = '';

    var chatOptions = '<div class="messenger-inline-header-options"> \
    <div class="minimize i-icon-minus"></div> \
    <div class="close  i-icon-remove "></div> \
    </div>';
    var header = '<div class="messenger-inline-chat-session-header"> \
    <span class="messenger-user-status status-' + online_status + '"></span> \
    <span class="messenger-inline-session-title">' + room_name + '</span>' + chatOptions + ' \
    </div>';
    var inputOptions = '<div class="messenger-inline-input-options"><div class="messenger-option-item messenger-chat-settings-icon icon-gear"></div></div>';
    var load_more = '<div class="messenger-load-more-messages i-text-center i-pointer click-now" \
      data-room_id="' + room_id + '" >load more messages</div>';
    var display = '';
    if (!opened) {
      display = 'style="display:none;"';
    }
    var content = '<div class="messenger-inline-flyout-content messenger-inline-room-content" ' + display + '> \
    <div class="content"> \
      <div class="chat-history scrollable"> \
        <div class="chat-history-header">' + load_more + '</div> \
        <div class="chat-history-content">' + messages+'</div> \
        <div class="chat-history-footer"></div> \
      </div> \
      <div id="' + chat_settings_id + '" class="chat-settings scrollable hidden"> \
          <div id="' + chat_settings_form_id + '"><div class="i-loading"></div></div></div> \
    </div> ' + inputOptions + ' \
    <textarea class="messenger-inline-text-area autosize" title="type here... & press ENTER" placeholder="type here... :-) & press ENTER"></textarea> \
    </div>';

    var flyout = '<div class="messenger-inline-chat-session-flyout">' + header + content + '</div>';

    var node = document.createElement('div');
    var classes = 'messenger-inline-chat-room';
    if (opened) {
      classes += ' opened';
    }
    
    classes += ' room-' + room_type;
    

    node.setAttribute('class', classes);
    node.setAttribute('id', panel_id);
    node.setAttribute('data-rid', room_id);
    node.innerHTML = flyout;
    
    IN.messenger.create_messenger_bottom_panel();
    
    panel_id = '#' + panel_id;
    
    if ($(panel_id + '-wrapper').length != 0) {
		$(panel_id + '-wrapper').html('');
		$(panel_id + '-wrapper').append($(node));
	} else {
		$('#messenger-inline-chat-room-wrapper').append($(node));
	}
	
    var panel_history = panel_id + ' .chat-history';

    $(panel_id).data('room_id', room_id);
    
    
    $(panel_id + ' .messenger-inline-chat-session-header').click(function(event) {

      if ($(panel_id + ' .messenger-inline-flyout-content').is(':visible')) {
        $(panel_id + ' .messenger-inline-flyout-content').stop().slideUp('fast'); // close
        $(panel_id).removeClass('opened');
      } else {
        $(panel_id + ' .messenger-inline-flyout-content').stop().slideDown('fast'); // show
        $(panel_id).addClass('opened');
        //session.focus(); close not working
      }
      IN.messenger.arrangeChatRooms();
    });
  
    $(panel_id + ' .close').click(function(event) {
        $(panel_id).addClass('closed');
        $(panel_id).appendTo($('#messenger-inline-chat-room-wrapper-hidden')); 
        
        // keep only some messages to keep browser not to hang
        var total = $(panel_id + ' .chat-history-content .Message').length;
        if (total > 50) {
		  $(panel_id + ' .chat-history-content .Message').slice(0, total - 50).remove();
		}
        
        var $message = $(panel_id + ' .chat-history-content .Message:first-child');
        
        var first_message_id = parseInt($message.data('id'));
        session.first_message_id = first_message_id;
        
        IN.messenger.arrangeChatRooms();
        event.preventDefault();
    });
	
    $(panel_id + ' .messenger-inline-text-area').bind('keydown', function(event) {
        if(!(event.keyCode == 13 && event.shiftKey == 0)) { // Enter key
            return;
        }
        
        var text = $(this).val();
        
        text = text.replace(/^\s+|\s+$/g, '');
        if (text != '') {
            var msg = {
                ws_action : 'messenger_send',
                message : text,
                room_id : room_id
            };
            IN.WS.send(msg);
            
            $(this).val('');
            $(this).focus();
            return false;
        }
    });
	$(panel_id + ' .chat-history-content').bind('mouseup', function(event) {
	  // TODO: blink off
	
	  var sel = '';
	  if (window.getSelection) {
	    sel = window.getSelection();
	  } else if (document.getSelection) {
	    sel = document.getSelection();
	  } else if (document.selection) {
	    sel = document.selection.createRange().text;
	  }
	  if (sel == '') {
	    $(panel_id + ' .messenger-inline-text-area').focus();
	  }
	});
	
	IN.messenger.arrangeChatRooms();
    
	IN.trigger('dom', true); // dom changed
  };
  
  IN.WSCommands.prototype.messenger_new_message = function(messages) {
    messages = messages.messages;
    
    for (var idx in messages) {
        var message = messages[idx];        
        var room = message.room;
        var room_id = room.id;
        if (!(room_id in IN.messenger.sessions)) {
            IN.WS.commands['init_session'](message);
        }
        
        var session = IN.messenger.sessions[room_id];
        session.post(message);
    }
    
    IN.messenger.arrangeChatRooms();
    
  };
  
  
  IN.WSCommands.prototype.messenger_rooms_state = function(messages) {
    messages = messages.messages;
    
    for (var idx in messages) {
      var message = messages[idx];        
      var room = message.room;
      var room_id = room.id;
      if (room_id in IN.messenger.sessions) {
        var session = IN.messenger.sessions[room_id];
        session.is_in_state_update = false;
        session.post(message);

      }
    }
    
    // remove state update flag
    for (var room_id in IN.messenger.sessions) {
      var session = IN.messenger.sessions[room_id];
      session.is_in_state_update = false;
      
      // post pendings
      for (var message in session.pending_messages) {
        session.post(message, message._prepend);
      }

    }
  };
  
  
  IN.WSCommands.prototype.messenger_room_messages_load_more = function(messages) {
    messages = messages.messages;
    
    for (var idx in messages) {
      var message = messages[idx];        
      var room = message.room;
      var room_id = room.id;
      if (room_id in IN.messenger.sessions) {
        var session = IN.messenger.sessions[room_id];
        session.post(message, true); // prepend
      }
    }
    
  };
  
  IN.WSCommands.prototype.messenger_notification_count = function(message) {
    var count = message.count;
    
    if (count == 0) {
	  var count_html = '<div class="count"></div>';
	} else {
	  var count_html = '<div class="count i-badge i-badge-notification i-badge-danger i-position-top-right i-text-truncate">' + count + '</div>';
	}
    $('.notification-count.message-count .count').replaceWith(count_html);
  };
  
  IN.messenger.create_messenger_bottom_panel = function() {
    if ($('#messenger-inline-chat-bottom-panel').length == 0) {
		var panel = '<div id="messenger-inline-chat-bottom-panel"> \
        <div id="messenger-inline-chat-more-wrapper"><div class="chat-more" data-i-dropdown=""><span class="count">1</span> \
          <div class="i-dropdown i-dropdown-up"></div> \
        </div></div> \
        <div id="messenger-inline-chat-room-wrapper"></div> \
        <div id="messenger-inline-chat-room-wrapper-hidden"></div></div>';
        $('body').append(panel);
        
        $('#messenger-inline-chat-more-wrapper .chat-more').on('show.uk.dropdown', function(){
          var menutext = '';
          $('#messenger-inline-chat-room-wrapper-hidden').children().each(function(){
            if (!$(this).hasClass('closed')) {
			  var room_id = $(this).data('room_id');
              menutext += '<li class="messenger-trigger" data-room_id="'+room_id+'">' + $(this).find('.messenger-inline-session-title').text() + '</li>';
            }
          });
          $('#messenger-inline-chat-more-wrapper .i-dropdown').html('<ul class="i-nav i-nav-dropdown">' + menutext + '</ul>');
          IN.trigger('dom', true);
        });
    }
  }


  IN.messenger.chatRoomSpaceAvailable = function(newroom) {
    if ($('#dummi-chat-room').length == 0) {
      $('body').append('<div id="dummi-chat-room" class="i-hidden messenger-inline-chat-room opened"></div>')
    }
    var morewidth = 50;
    var windowwidth = $(window).width();
    var newwidth = $('#dummi-chat-room').outerWidth(true);
    var roomwidth = $('#messenger-inline-chat-room-wrapper').outerWidth(true);

    var total = roomwidth + morewidth;
    if (newroom) {
      total += newwidth;
    }
    return (windowwidth > total);
  }

  IN.messenger.arrangeChatRooms = function() {
    if (this.onwork) { // stop multiple
      return;
    }
    this.onwork = true;
    var room = $('#messenger-inline-chat-room-wrapper');
    var more = $('#messenger-inline-chat-more-wrapper');
    var hidden = $('#messenger-inline-chat-room-wrapper-hidden');

    while(!IN.messenger.chatRoomSpaceAvailable(false)) {
      var children = room.children();
      if (children.length == 0) { break; }
      children.filter(':last').appendTo(hidden);
    }

    var count = hidden.children().not('.closed').length;

    while(IN.messenger.chatRoomSpaceAvailable(true)) {
      var children = hidden.children().not('.closed');
      if (children.length == 0) { break; }
      children.filter(':last').appendTo(room);
    }
    var count = hidden.children().not('.closed').length;
    more.find('.count').html(count);
    if (count != 0) {
      more.show();
      //DSN.Chat._moreChatBlink();
    } else {
      more.hide();
      //DSN.util.blink(more, false);
    }

    this.onwork = false;
  }

  IN.messenger.arrangeChatRooms.onwork = false;

  $(window).bind('resize', function() {
    IN.messenger.arrangeChatRooms();
  });

})(jQuery);
  
  return IN.messenger;
  
});
