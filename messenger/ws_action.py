
@IN.hook
def ws_action_messenger_init_session(context, message):
	
	from_nabar_id = context.nabar.id
	
	if not from_nabar_id:
		return
	
	room = None
	messenger = IN.messenger
	
	if 'to_nabar_id' in message:
		to_nabar_id = message['to_nabar_id']
		if not to_nabar_id:
			return
		if messenger.message_access(from_nabar_id, to_nabar_id):
		
			room = messenger.get_su_room_between(from_nabar_id, to_nabar_id)
			if not room:
				room = messenger.create_su_room(from_nabar_id, to_nabar_id)
			
	elif 'room_id' in message:
		room_id = int(message['room_id'])
		if not room_id:
			return
		room = IN.entitier.load_single('Room', room_id)
	
	if not room:
		return
	
	
	if not room.access('send', from_nabar_id):
		return
	
	message = {
		'ws_command' : 'init_session',
		'room' : {
			'id' : room.id,
			'name' : room.get_title(from_nabar_id),
			'type' : room.type
		}
	}
	
	if room.type == 'su':
		# set to_nabar_id
		if room.members[0] == from_nabar_id:
			message['to_nabar_id'] = room.members[1]
		else:
			message['to_nabar_id'] = room.members[0]
		
	# TODO: ACCESS CHECK
	context.send(message)
	

@IN.hook
def ws_action_messenger_send(context, message):
	
	if not message['message']:
		return
	
	if not message['room_id']:
		return
	
	room_id = message['room_id']
	
	# TODO: access check
	
	room = IN.entitier.load_single('Room', room_id)
	
	if not room:
		raise Exception('Room not found!')
	
	if not room.access('send', context.nabar.id):
		return
	
	messenger = IN.messenger
	
	message = messenger.send_text_message_to_room(message['message'], room, context.nabar)
	
	if not message:
		return
		
	# send themed message
	
	send_message = {
		'message' : {
			'id' : message.id,
			'message' : IN.themer.theme(message, args = {
				'context' : context
			}),
			'nabar_id' : message.nabar_id,
			'read_status' : 1,
		},
		'room' : {
			'id' : room.id,
			'name' : room.get_title(context.nabar.id),
			'type' : room.type
		}
	}
	
	ws_message = {
		'ws_command' : 'messenger_new_message',
		'messages' : [send_message]
	}
	
	# TODO: send to all public room members
	if room.type == 'public':
		
		subscriptions = IN.APP.context_subscriptions
		contexts = IN.APP.contexts
		
		if room.id not in subscriptions:
			return
		
		for nabar_id in subscriptions[room.id]:
		
			for nabar_context in contexts[nabar_id]:
				try:
					nabar_context.send(ws_message)
				except Exception as e:
					IN.logger.debug()
	else:
		
		contexts = IN.APP.contexts
		
		for nabar_id in room.members:
			if nabar_id in contexts:
				for nabar_context in contexts[nabar_id]:
					try:
						nabar_context.send(ws_message)
					except Exception as e:
						IN.logger.debug()

@IN.hook
def ws_action_messenger_rooms_state(context, message):
	
	if 'rooms_state' not in message:
		return
	
	rooms_state = message['rooms_state']
	
	if not rooms_state:
		return
	
	# TODO: ACCESS CHECK for each room
	
	where = []
	
	for room_id, last_message_id in rooms_state.items():
		where.append(['and', [['room_id', room_id], ['id', '>', last_message_id], ['status', 1]]])
	
	try:
		
		cursor = IN.db.select({
			'table' : 'message.message',
			'columns' : ['id'],
			'where' : ['OR', where],
			'order' : 'created'
		}).execute()
		
		messages = []
		
		if cursor.rowcount != 0:
			ids = [data['id'] for data in cursor]
			
			message_entities = IN.entitier.load_multiple('Message', ids)
			read_status = IN.messenger.get_message_read_status(ids, context.nabar.id)
			
			so = sorted(message_entities.values(), key = lambda o : o.id)
			
			__theme = IN.themer.theme
			args = {'context' : context}
			
			for message_entity in so:
				id = message_entity.id
				messages.append({				
					'message' : {
						'id' : id,
						'message' : __theme(message_entity, args = args),
						'nabar_id' : message_entity.nabar_id,
						'read_status' : read_status.get(id, 2)
					},
					'room' : {
						'id' : message_entity.room_id,
					}
				})
			
		try:
			context.send({
				'ws_command' : 'messenger_rooms_state',
				'messages' : messages
			})
		except Exception as e1:
			IN.logger.debug()
			
	except Exception as e:
		IN.logger.debug()
	
@IN.hook
def ws_action_messenger_room_messages_load_more(context, message):
	
	# TODO: ROOM ACCESS
	
	if 'room_id' not in message:
		return
	
	room_id = message['room_id']
	
	first_message_id = 0;
	if 'first_message_id' in message:
		first_message_id = message['first_message_id']
	
	try:
		where = [
			['room_id', room_id],
			['status', 1],
		]
		
		if first_message_id > 0:
			where.append(['id', '<', first_message_id])
		
		cursor = IN.db.select({
			'table' : 'message.message',
			'columns' : ['id'],
			'where' : where,
			'order' : {'created' : 'desc'},
			'limit' : 15,
		}).execute()
		
		messages = []
		
		if cursor.rowcount != 0:
			ids = [data['id'] for data in cursor]
			
			message_entities = IN.entitier.load_multiple('Message', ids)
			
			read_status = IN.messenger.get_message_read_status(ids, context.nabar.id)
			
			so = sorted(message_entities.values(), key = lambda o : o.id, reverse=True)
			
			__theme = IN.themer.theme
			args = {'context' : context}
			
			for message_entity in so:
				id = message_entity.id
				messages.append({
					'message' : {
						'id' : id,
						'message' : __theme(message_entity, args = args),
						'nabar_id' : message_entity.nabar_id,
						'read_status' : read_status.get(id, 2)
					},
					'room' : {
						'id' : message_entity.room_id,
					}
				})
			
		try:
			context.send({
				'ws_command' : 'messenger_room_messages_load_more',
				'messages' : messages
			})
		except Exception as e1:
			IN.logger.debug()
			
	except Exception as e:
		IN.logger.debug()
	

@IN.hook
def ws_action_messenger_mark_read(context, message):
	
	if 'ids' not in message:
		return
	
	ids = message['ids']
	
	if not ids:
		return
	
	try:
		
		IN.db.update({
			'table' : 'message.message_nabar',
			'set' : [['status', 2]],  # read
			'where' : [
				['nabar_id', context.nabar.id],
				['message_id', 'IN', ids]
			]
		}).execute()
		
		IN.db.connection.commit()
		
	except Exception as e:
		IN.db.connection.rollback()
		IN.logger.debug()

@IN.hook
def ws_action_messenger_notification_count(context, message):
	try:
		nabar_id = context.nabar.id
		
		if not nabar_id:
			return
			
		
		cursor = IN.db.select({
			'table' : ['message.message_nabar', 'mn'],
			'count_column' : 'distinct m.room_id',
			'join' : [
				['inner join', 'message.message', 'm', [
					['mn.message_id = m.id']
				]]
			],
			'where' : [
				['mn.nabar_id', nabar_id],
				['mn.status', 1],
				['m.status', '>=', 1],
			],
		}).execute_count()
		
		if cursor.rowcount == 0:
			return
		
		count = cursor.fetchone()[0]
		
		context.send({
			'ws_command' : 'messenger_notification_count',
			'count' : count
		})
		
	except Exception as e:
		IN.logger.debug()


@IN.hook
def ws_action_messenger_subscribe(context, message):
	try:
		
		subscriptions = IN.APP.context_subscriptions
		key = message['key']
		if key not in subscriptions:
			subscriptions[key] = set()
		
		subscriptions[key].add(context.nabar.id)
		
	except Exception as e:
		IN.logger.debug()


@IN.hook
def ws_action_messenger_unsubscribe(context, message):
	try:
		
		subscriptions = IN.APP.context_subscriptions
		key = message['key']
		if key not in subscriptions:
			return
		
		subscriptions[key].remove(context.nabar.id)
		
	except Exception as e:
		IN.logger.debug()
