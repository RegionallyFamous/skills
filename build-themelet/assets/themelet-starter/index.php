<?php
/**
 * Static front page for the themelet starter.
 */

defined( 'ABSPATH' ) || exit;
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
	<a class="skip-link" href="#main">Skip to content</a>

	<main id="main" class="themelet-main">
		<section class="themelet-hero" aria-labelledby="themelet-title">
			<div class="themelet-copy">
				<p class="eyebrow">Themelet Starter</p>
				<h1 id="themelet-title">A static site in WordPress clothing.</h1>
				<p>
					Replace this markup with the static HTML experience. Keep WordPress integration
					small, visible, and boring.
				</p>
			</div>
			<img src="<?php echo themelet_starter_asset( 'themelet-mark.svg' ); ?>" alt="" width="320" height="320">
		</section>
	</main>

	<?php wp_footer(); ?>
</body>
</html>
