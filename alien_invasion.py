import sys
from time import sleep

import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
	"""Overall class to manage game assets and behavior."""

	def __init__(self):
		"""Initialize the game, and create game resource."""
		pygame.init()
		self.settings = Settings()

		# Full screen mode
		# self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
		# self.settings.screen_width = self.screen.get_rect().width
		# self.settings.screen_height = self.screen.get_rect().height

		# self.screen = pygame.display.set_mode((1200, 800))
		self.screen = pygame.display.set_mode(
			(self.settings.screen_width, self.settings.screen_height))
		pygame.display.set_caption("Alien Invasion")

		# Create an instance to store game statistics, and create a scoreboard

		# Create an instance to store game statistics.
		self.stats = GameStats(self)
		self.sb = Scoreboard(self)

		"""Set the background color."""
		# self.bg_color = (230, 230, 230)

		self.ship = Ship(self)
		self.bullets = pygame.sprite.Group()
		self.aliens = pygame.sprite.Group()

		self._create_fleet()

		# Make the play button
		self.play_button = Button(self, 'Play')

	def run_game(self):
		"""Start the main loop for the game."""
		while True:
			"""Watch for keyboard and mouse events."""
			self._check_events()
			# for event in pygame.event.get():
			# 	if event.type == pygame.QUIT:
			# 		sys.exit()

			# self.ship.update()

			# self.bullets.update()

			# # Get rid of bullets that have disappeared.
			# for bullet in self.bullets.copy():
			# 	if bullet.rect.bottom <= 0:
			# 		self.bullets.remove(bullet)
			# # print(len(self.bullets))
			# self._update_bullets()

			# self._update_aliens()

			if self.stats.game_active:
				self.ship.update()
				self._update_bullets()
				self._update_aliens()

			self._update_screen()
			"""Redraw the screem during each pass through the loop."""
			# self.screen.fill(self.bg_color)
			# self.screen.fill(self.settings.bg_color)
			# self.ship.blitme()

			"""Make the most recently drawn screen visible."""

	# pygame.display.flip()

	def _check_events(self):
		"""Respond to keypress and mouse events."""

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

			elif event.type == pygame.KEYDOWN:

				# if event.key == pygame.K_RIGHT:
				# 	# Move the ship to the right.
				# 	# self.ship.rect.x += 1
				# 	self.ship.moving_right = True
				#
				# elif event.key == pygame.K_LEFT:
				# 	self.ship.moving_left = True
				self._check_keydown_events(event)

			elif event.type == pygame.KEYUP:

				# if event.key == pygame.K_RIGHT:
				# 	self.ship.moving_right = False
				#
				# elif event.key == pygame.K_LEFT:
				# 	self.ship.moving_left = False
				self._check_keyup_events(event)

			elif event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos()
				self._check_play_button(mouse_pos)

	def _check_play_button(self, mouse_pos):
		"""Start a new game when the player clicks play."""
		button_clicked = self.play_button.rect.collidepoint(mouse_pos)
		# if self.play_button.rect.collidepoint(mouse_pos):
		if button_clicked and not self.stats.game_active:
			# Reset the game settings.
			self.settings.initialize_dynamic_settings()

			# self.stats.game_active = True
			# Reset the game statistics
			self.stats.reset_stats()
			self.stats.game_active = True
			self.sb.prep_score()
			self.sb.prep_level()
			self.sb.prep_ship()

			# Get rid of any remaining aliens and bullets.
			self.aliens.empty()
			self.bullets.empty()

			# Create a new fleet and center the ship
			self._create_fleet()
			self.ship.center_ship()

			# Hide the mouse cursor.
			pygame.mouse.set_visible(False)

	def _check_keydown_events(self, event):
		"""Respond to keypress"""
		if event.key == pygame.K_RIGHT:
			self.ship.moving_right = True
		elif event.key == pygame.K_LEFT:
			self.ship.moving_left = True
		elif event.key == pygame.K_q:
			sys.exit()
		elif event.key == pygame.K_SPACE:
			self._fire_bullet()

	def _check_keyup_events(self, event):
		"""Respond to kye releases."""
		if event.key == pygame.K_RIGHT:
			self.ship.moving_right = False
		if event.key == pygame.K_LEFT:
			self.ship.moving_left = False

	def _fire_bullet(self):
		"""Create a new bullet and add it to the bullets group."""
		if len(self.bullets) < self.settings.bullets_allowed:
			new_bullet = Bullet(self)
			self.bullets.add(new_bullet)

	def _update_bullets(self):
		"""Update position of bullets and get rid of old bullets."""
		# Update bullet positions.
		self.bullets.update()

		# Get rid of bullets that have disappeared
		for bullet in self.bullets.copy():
			if bullet.rect.bottom <= 0:
				self.bullets.remove(bullet)

		# check for any bullets that have hit aliens.
		# If so, get rid of the bullet and the alien.
		# collisions = pygame.sprite.groupcollide(self.bullets, self.aliens,
		# 										True, True)

		# if not self.aliens:
		# 	# Destroy existing bullets and creat new fleet.
		# 	self.bullets.empty()
		# 	self._create_fleet()

		self._check_bullet_alien_collisions()

	def _check_bullet_alien_collisions(self):
		"""Respond to bullet-alien collisions."""
		# Remove ant bullets and aliens that have collided.
		collisions = pygame.sprite.groupcollide(self.bullets, self.aliens,
												True, True)

		if collisions:
			# self.stats.score += self.settings.alien_points
			for aliens in collisions.values():
				self.stats.score += self.settings.alien_points * len(aliens)
			self.sb.prep_score()
			self.sb.check_high_score()

		if not self.aliens:
			# Destroy the existing bullets and create an new fleet
			self.bullets.empty()
			self._create_fleet()
			self.settings.increase_speed()

			# Increase level.
			self.stats.level += 1
			self.sb.prep_level()

	def _update_aliens(self):
		# """Update the position of all aliens in the fleet"""
		"""Check if the fleet is at an edge, then update position of all
		aliens in the fleet."""
		self._check_fleet_edges()
		self.aliens.update()

		# Look for alien-ship collisions.
		if pygame.sprite.spritecollideany(self.ship, self.aliens):
			# print('Ship hit!!!')
			self._ship_hit()

		# Look for aliens hitting the bottom of the screen
		self._check_aliens_bottom()

	def _check_fleet_edges(self):
		"""Respond appropriately if any aliens have reached an edge"""
		for alien in self.aliens.sprites():
			if alien.check_edges():
				self._change_fleet_direction()
				break

	def _change_fleet_direction(self):
		"""Drop the entire fleet and change the fleet's direction."""
		for alien in self.aliens.sprites():
			alien.rect.y += self.settings.fleet_drop_speed
		self.settings.fleet_direction *= -1

	def _create_fleet(self):
		"""Create the fleet of the aliens."""
		# Make an alien.
		# alien = Alien(self)
		# self.aliens.add(alien)

		# Create an alien and find the number of aliens in a row.
		# Spacing between each alien is equal to one alien width.
		alien = Alien(self)
		# alien_width = alien.rect.width
		alien_width, alien_height = alien.rect.size
		available_space_x = self.settings.screen_width - (2 * alien_width)
		number_aliens_x = available_space_x // (2 * alien_width)

		# Determine the number of rows of aliens that fit on the screen
		ship_height = self.ship.rect.height
		available_space_y = self.settings.screen_height - (3 * alien_height) \
							- ship_height
		number_rows = available_space_y // (2 * alien_height)

		# Create the first row of aliens.
		# Create full fleets of aliens.
		for row_number in range(number_rows):
			for alien_number in range(number_aliens_x):
				# Create an alien and place it in the row
				# alien = Alien(self)
				# alien.x = alien_width + 2 * alien_width * alien_number
				# alien.rect.x = alien.x
				# self.aliens.add(alien)
				self._create_alien(alien_number, row_number)

	def _ship_hit(self):
		"""Respond to the ship being hit by an alien"""

		if self.stats.ship_left > 0:
			# Decrement ship_left, and update the scoreboard
			self.stats.ship_left -= 1
			self.sb.prep_ship()

			# Get rid of any remaining aliens and bullets
			self.aliens.empty()
			self.bullets.empty()

			# Create a new fleet and center the ship.
			self._create_fleet()
			self.ship.center_ship()

			# pause
			sleep(0.5)

		else:
			self.stats.game_active = False
			pygame.mouse.set_visible(True)

	def _check_aliens_bottom(self):
		"""Check if any alien have reached the bottom of the screen."""
		screen_rect = self.screen.get_rect()
		for alien in self.aliens.sprites():
			if alien.rect.bottom >= screen_rect.bottom:
				# Treat this same as if the ship got hit
				self._ship_hit()
				break

	def _create_alien(self, alien_number, row_number):
		"""Create an alien and place it in the row."""
		alien = Alien(self)
		# alien_width = alien.rect.width
		alien_width, alien_height = alien.rect.size
		alien.x = alien_width + 2 * alien_width * alien_number
		alien.rect.x = alien.x
		alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
		self.aliens.add(alien)

	def _update_screen(self):
		"""Update the image of the screen, and flip to the new screen."""
		self.screen.fill(self.settings.bg_color)
		self.ship.blitme()

		for bullet in self.bullets.sprites():
			bullet.draw_bullet()

		self.aliens.draw(self.screen)

		# Draw the screen information.
		self.sb.show_score()

		# Draw the play button if the game is inactive.
		if not self.stats.game_active:
			self.play_button.draw_button()

		pygame.display.flip()


if __name__ == "__main__":
	"""Make a game instance, and run the game."""
	ai = AlienInvasion()
	ai.run_game()
