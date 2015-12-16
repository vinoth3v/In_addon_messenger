from In.boxer.box import Box, BoxThemer

class BoxMessagesList(Box):
	''''''
	title = s('Messages')


@IN.register('BoxMessagesList', type = 'Themer')
class BoxMessagesListThemer(BoxThemer):


	def theme_items(self, obj, format, view_mode, args):
		
		obj.css.append('i-overflow-container')
		
		data = {
			'lazy_args' : {
				'load_args' : {
					'data' : {
					},
				}
			},
		}
		
		obj.add('MessageListLazy', data)
		
		super().theme_items(obj, format, view_mode, args)
