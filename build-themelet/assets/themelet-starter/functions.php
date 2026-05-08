<?php
/**
 * Themelet starter setup.
 */

defined( 'ABSPATH' ) || exit;

const THEMELET_STARTER_VERSION = '1.0.0';

add_action( 'after_setup_theme', 'themelet_starter_setup' );
add_action( 'wp_enqueue_scripts', 'themelet_starter_enqueue_assets' );

function themelet_starter_setup(): void {
	add_theme_support( 'title-tag' );
	add_theme_support( 'html5', [ 'script', 'style' ] );
}

function themelet_starter_enqueue_assets(): void {
	wp_enqueue_style(
		'themelet-starter-site',
		get_template_directory_uri() . '/site.css',
		[],
		THEMELET_STARTER_VERSION
	);
}

function themelet_starter_asset( string $path ): string {
	return esc_url( get_template_directory_uri() . '/assets/' . ltrim( $path, '/' ) );
}
