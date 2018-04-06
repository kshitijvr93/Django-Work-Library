<?php
/*
 * Plugin Name: HSCLib Data Management
 * Plugin URI: tbd
 * Description: Display a data management interactive graphic.
 * Author: Robert Vernon Phillips
 * Version: 1.0
 * Author URI: tbd
 */

/* Initial WordPress Version check */
global $wp_version;

$exit_msg='HSCLib_Data_Management: This requires WordPress 2.8 or newer.
<a href="http://codex.wordpress.org/Upgrading_WordPress">Please
update!</a>';
if (version_compare($wp_version,"2.8","<"))
{
    exit ($exit_msg);
}

/**
 * HSCLib_Data_Management plugin widget.
 * Display a data management interactive graphic.
 */
class HSCLib_Data_Management extends WP_Widget {

	public static $params = array(
		// Value for key 'id-base' must be unique within the WordPress site's 'id-base' keys;
		// and for real-life use, unique also should be the the values for keys 'name_config_page_en'
		// and 'wo_description_en' among the respective keys among all WordPress site widgets.
		'id-base'             => 'HSCLib_Data_Management' ,
		// English config page name: shows under wp-admin/Appearance/Widgets display
		'name_config_page_en' => 'HSCLib Data Management' ,
	);

	// Define all widget options, and strings in English here.
	// The constructor should automatically internationalize any values needed.
	public static $widget_os = array(
			// Widget option: description
		'description_en'   =>
		'UF HSC Library Data Management Widget.',
	);

	/**
	 * Register widget with WordPress.
	 */
	function __construct() {

		$widget_opts = array(
			'description' => __(
				HSCLib_Data_Management::$widget_os['description_en'], 'text_domain' ),
		);
		parent::__construct(
			// Base ID
			HSCLib_Data_Management::$params['id-base'],
			// Config Page Name for display is next.
			// Note: cannot call __() to compute a class-initialized value in $params,
			// so we do it here. Also, 'text_domain' need not vary now so we hard code it here.
			__( HSCLib_Data_Management::$params['name_config_page_en'], 'text_domain' ),
			// array of args, also called Widget Options
			$widget_opts
			// No control options need to be passed for this class.
		);
	}

	/**
	 * Front-end display of widget.
	 *
	 * @see WP_Widget::widget()
	 *
	 * @param array $args     Widget arguments.
	 * @param array $instance Saved values from database.
	 */
	public function widget( $args, $instance ) {

		// Consider implementing administrable settings if changes
		// are frequently required, or if a more generic widget is useful.
		// For now, set widget-width at 256, which seems not uncommon among sidebars...
		// and can put into an administrable option later
		// See www.w3.org/TR/SVG/ for docs on <svg> containers
		// and sub-elements.

		echo $args['before_widget'];
		if ( ! empty( $instance['title'] ) ) {
			echo $args['before_title'] . apply_filters( 'widget_title', $instance['title'] )
				. $args['after_title'];
		}
    ?>
		<div style="line-height:1.2em;">
		<p style="line-height:1.6vw;font-size:1.6vw"><strong>The Research Data Life Cycle</strong></p>
		<svg id="hsclib_dmgt_svg" width="100%"  viewbox="0 0 100 100">
			<defs><polygon id="arrowhead" points="0,0 4,12 8,0 4,4" stroke-width="1%" stroke="yellow" /></defs>

		  <g class="gd_detail" >
		  <rect></rect>
		  <rect></rect>
		  </g>

		  <g class="gd_idea">
		  	<rect></rect>
				<use class="arrow" xlink:href="#arrowhead" fill="navy"
					transform="translate(67 17) rotate(315 4,6) "/>
		  	<text class="title">Idea</text>
		  	<text class="detail" visibility="hidden">Locate</text>
		  	<text class="detail" visibility="hidden">researchers,</text>
		  	<text class="detail" visibility="hidden">datasets,</text>
		  	<text class="detail" visibility="hidden">funding</text>
		  	<text class="detail" visibility="hidden">opportunites.</text>
				<rect onClick="window.location.href='http://cms.uflib.ufl.edu/datamgmt/idea'"> </rect>
		  </g>
		  <g class="gd_plan" >
		  	<rect></rect>
				<use class="arrow" xlink:href="#arrowhead" fill="navy"
					transform="translate(80 57) rotate(15 4,6) "/>
		  	<text class="title">Plan</text>
		  	<text class="detail"  visibility="hidden">Use UF's</text>
		  	<text class="detail"  visibility="hidden">DMPTool, or</text>
		  	<text class="detail"  visibility="hidden">browse example</text>
		  	<text class="detail"  visibility="hidden">text, to create</text>
		  	<text class="detail"  visibility="hidden">your own Data</text>
		  	<text class="detail"  visibility="hidden">Management</text>detail
		  	<text class="detail"  visibility="hidden">Plan.</text>
				<rect onClick="window.location.href='http://cms.uflib.ufl.edu/datamgmt/plan'"></rect>
		  </g>

		  <g class="gd_collect" >
		  	<rect></rect>
				<use class="arrow" xlink:href="#arrowhead" fill="navy"
					transform="translate(47 80) rotate(90 4,6) "/>
		  	<text class="title">Collect</text>
		  	<text class="title">Data</text>
		  	<text class="detail"  visibility="hidden">Collect and</text>
		  	<text class="detail"  visibility="hidden">document your</text>
		  	<text class="detail"  visibility="hidden">data. Find</text>
		  	<text class="detail"  visibility="hidden">software and</text>
		  	<text class="detail"  visibility="hidden">support tools.</text>
				<rect onClick="window.location.href='http://cms.uflib.ufl.edu/datamgmt/collect'"></rect>
		  </g>

		  <g class="gd_analyze" >
		  	<rect></rect>
				<use class="arrow" xlink:href="#arrowhead" fill="navy"
					transform="translate(15 57) rotate(165 4,6)" />
		  	<text class="title">Analyze</text>
		  	<text class="title">Data</text>
		  	<text class="detail"  visibility="hidden">Discover</text>
		  	<text class="detail"  visibility="hidden">visualization and</text>
		  	<text class="detail"  visibility="hidden">text mining tools.</text>
		  	<text class="detail"  visibility="hidden">Identify experts</text>
		  	<text class="detail"  visibility="hidden">and consultants</text>
		  	<text class="detail"  visibility="hidden">on campus.</text>
				<rect onClick="window.location.href='http://cms.uflib.ufl.edu/datamgmt/analyze'"></rect>
		  </g>

		  <g class="gd_share" >
		  	<rect></rect>
				<use class="arrow" xlink:href="#arrowhead" fill="navy"
					transform="translate(23 16) rotate(225 4,6) "/>
			  <text class="title">Share</text>
			  <text class="title">Data</text>
			  <text class="detail"  visibility="hidden">Learn how to</text>
			  <text class="detail"  visibility="hidden">share your data</text>
			  <text class="detail"  visibility="hidden">using available</text>
			  <text class="detail"  visibility="hidden">standards and</text>
			  <text class="detail"  visibility="hidden">resources.</text>
				<rect onClick="window.location.href='http://cms.uflib.ufl.edu/datamgmt/share'"></rect>
		  </g>

		</svg>
    <!-- use only for local testing of scaling
		</svg>
    -->

		<p style="line-height:1.6vw;font-size:1.6vw"><strong>Research Data Management Support</strong></p>
		<p style="margin-top:-2%; font-size:1.2vw;">
    The University of Florida Libraries are here to assist you with data
		management planning, including the development of data management plans,
		supporting long term preservation needs, improving data discoverability,
		and meeting UF security and privacy requirements.</p>
		<p style="line-height:1.6vw;font-size:1.6vw"><strong>Why manage research data?</strong></p>
		<ul style="list-style-type: circle; font-size:1.2vw; list-style-position: inside; line-height:0.5em" >
		    <li style="margin-top:-2%;margin-left:5%;text-indent:-1%;">Save time&nbsp;</li>
		    <li style="margin-left:5%;text-indent:-1%;">Meet funding requirements</li>
		    <li style="margin-left:5%;text-indent:-1%;">Increase discovery and reuse</li>
		    <li style="margin-left:5%;text-indent:-1%;">Protect and preserve data</li>
		</ul>

		<script type="text/javascript">
    var svg = document.getElementsByTagName("svg")[0];
		var gd_idea = svg.getElementsByClassName("gd_idea")[0];
		var gd_plan = svg.getElementsByClassName("gd_plan")[0];
		var gd_collect = svg.getElementsByClassName("gd_collect")[0];
		var gd_analyze = svg.getElementsByClassName("gd_analyze")[0];
		var gd_share = svg.getElementsByClassName("gd_share")[0];
		var gd_detail = svg.getElementsByClassName("gd_detail")[0];

    function setGroupBox(gd) {
			rects = gd.getElementsByTagName('rect');
			rect0 = rects[0];
			rect1 = rects[1];
			var rx = new String("19%");
			var ry = new String("9%") ;

			details = gd.getElementsByClassName('detail');
			titles = gd.getElementsByClassName('title');

			rect1.setAttribute("height", "20%");
		  rect1.setAttribute("width", "30%");

		  rect0.setAttribute("fill", "navy");
			rect0.setAttribute("stroke-width", "1%");
			rect0.setAttribute("stroke", "yellow");

      // transparent for every rect1 in a group
		  rect1.setAttribute("fill", "transparent");

			rect0.setAttribute("rx", rx);
			rect1.setAttribute("rx", rx);

			rect0.setAttribute("ry", ry);
			rect1.setAttribute("ry", ry);

	  	rect0.setAttribute("height", "20%");
	  	rect1.setAttribute("height", "20%");

	  	rect0.setAttribute("width", "30%");
	  	rect1.setAttribute("width", "30%");

		  rect1.addEventListener("mouseover", mouseOver);
		  rect1.addEventListener("mouseout", mouseOut);

			if (gd == gd_idea) {
				rect0.setAttribute("x", "34%");
				rect1.setAttribute("x", "34%");
				rect0.setAttribute("y", "2%");
				rect1.setAttribute("y", "2%");

				titles[0].setAttribute("y", "15%");
        titles[0].setAttribute("x", "39%");
				titles[0].setAttribute("font-size", ".8em");
				titles[0].setAttribute("fill", "#ffffff");

			} else if (gd == gd_plan) {
				rect0.setAttribute("x", "70%");
				rect1.setAttribute("x", "70%");
				rect0.setAttribute("y", "30%");
				rect1.setAttribute("y", "30%")

				// Shrink this one a bit so display box does not overlap
	  		rect0.setAttribute("width", "27%");
	  		rect1.setAttribute("width", "27%");

        titles[0].setAttribute("x", "73%");
				titles[0].setAttribute("y", "43%");
				titles[0].setAttribute("font-size", ".8em");
				titles[0].setAttribute("fill", "#ffffff");
			} else if ( gd == gd_share) {
				rect0.setAttribute("x", "2%");
				rect1.setAttribute("x", "2%");
				rect0.setAttribute("y", "30%");
				rect1.setAttribute("y", "30%");

        titles[0].setAttribute("x", "8%");
				titles[0].setAttribute("y", "38%");
				titles[0].setAttribute("font-size", ".5em");
				titles[0].setAttribute("fill", "#ffffff");

        titles[1].setAttribute("x", "8%");
				titles[1].setAttribute("y", "45%");
				titles[1].setAttribute("font-size", ".5em");
				titles[1].setAttribute("fill", "#ffffff");

			} else if (gd == gd_collect) {
				rect0.setAttribute("y", "75%");
				rect0.setAttribute("x", "65%");
				rect1.setAttribute("y", "75%");
				rect1.setAttribute("x", "65%");

				titles[0].setAttribute("y", "83%");
        titles[0].setAttribute("x", "70%");
				titles[0].setAttribute("font-size", ".5em");
				titles[0].setAttribute("fill", "#ffffff");

				titles[1].setAttribute("y", "90%");
        titles[1].setAttribute("x", "70%");
				titles[1].setAttribute("font-size", ".5em");
				titles[1].setAttribute("fill", "#ffffff");

			} else if (gd == gd_analyze) {
				rect0.setAttribute("x", "9%");
				rect1.setAttribute("x", "9%");
				rect0.setAttribute("y", "75%");
				rect1.setAttribute("y", "75%");

        titles[0].setAttribute("x", "13%");
				titles[0].setAttribute("y", "83%");
				titles[0].setAttribute("font-size", ".5em");
				titles[0].setAttribute("fill", "#ffffff");

				titles[1].setAttribute("y", "90%");
        titles[1].setAttribute("x", "12%");
				titles[1].setAttribute("font-size", ".5em");
				titles[1].setAttribute("fill", "#ffffff");

			} else if (gd == gd_detail) {
				rect0.setAttribute("x", "33%");
				rect1.setAttribute("x", "33%");
				rect0.setAttribute("y", "30%");
				rect1.setAttribute("y", "30%");
				// Make detail box taller to hold more text
			  rect0.setAttribute("height", "40%");
				rect0.setAttribute("width", "36%");
				rect0.setAttribute("ry", "2%");
			  rect0.setAttribute("rx", "2%");

				// Set color of 'color box', rect0
				rect0.setAttribute("fill", "transparent");

				// Hide it at first
				rect0.setAttribute("visibility", "hidden");
			}
    } // end setGroupBox

		setGroupBox(gd_detail);
		setGroupBox(gd_idea);
		setGroupBox(gd_plan);
		setGroupBox(gd_collect);
		setGroupBox(gd_analyze);
		setGroupBox(gd_share);

		function mouseOver() {
			// get r_detail in which to change background color
			// and put detail texts.
			gd = this.parentNode
			svg = gd.parentNode
			gd_detail = svg.getElementsByClassName("gd_detail")[0];
			gdd_rects = gd_detail.getElementsByTagName('rect');
			// Don't do anything on mouseOver if this is the 'detail' rectangle:
			if ( this == gdd_rects[1]) return;

			// Change color of background rect
      r_background = gd.getElementsByTagName('rect')[0];
			r_background.style.fill = 'red';
			arrow = gd.getElementsByClassName('arrow')[0];
			arrow.style.fill = 'red';

      // For detail rect: show details
			gdd_rects[0].style['stroke-width'] = '.5%';
			gdd_rects[0].style.stroke = 'rgb(0,0,0)';

			gdd_rects[0].setAttribute("fill", "white");
		  gdd_rects[0].style.visibility = 'visible';

			// show detail text
			// See setGroupBox for details for starting x and y vals.
			// x=35%, y=27%, height = 42%
			//
			// adding margins for x and y of 2% and 7% to start the loop
			texts = gd.getElementsByClassName("detail");
			y = 37;
			for (var i = 0; i < texts.length; i++) {
				t = texts[i];
				t.setAttribute('visibility', 'visible');
				t.setAttribute('x', '34%');
				t.setAttribute('y', y.toString() + "%");
				t.setAttribute('font-size', '.35em');
				t.setAttribute('fill', 'black');
				t.setAttribute('color', 'black');
				y += 5
			}
		}

		function mouseOut() {
			gd = this.parentNode
			rects = gd.getElementsByTagName('rect');
			// Change r_detail background to transparent
			gd_detail = gd.parentNode.getElementsByClassName("gd_detail")[0];
			gd_rects = gd_detail.getElementsByTagName('rect');
			// Don't do anything on mouseOut if this is the 'detail' rectangle:
			if ( this == gd_rects[1]) return;

			rects[0].style.fill = 'navy';
			arrow = gd.getElementsByClassName('arrow')[0];
			arrow.style.fill = 'navy';

      // Set transparent background color of detail rect
			//gd_rects[0].style.fill = 'transparent';
			gd_rects[0].style.visibility = 'hidden';

			// hide details
			texts = gd.getElementsByClassName("detail");
			for (var i = 0; i < texts.length; i++) {
				t = texts[i];
				t.setAttribute('x', '0%');
				t.setAttribute('y', '0%');
				t.setAttribute('visibility', 'hidden');
			}
		}
		</script>
    </div>
    <?php
		echo $args['after_widget'];
	}

	/**
	 * Back-end widget form.
	 *
	 * @see WP_Widget::form()
	 * @see http://www.lynda.com/WordPress-tutorials/Enabling-configuration-widgets/68626/76300-4.html
	 *  "Enabling Configuration of Widgets"	at minutes:seconds of 1:20.
	 *
	 * @param array $instance Previously saved values from database.
	 */
	public function form( $instance ) {
		$title = ! empty( $instance['title'] ) ? $instance['title']
			: __( 'New title', 'text_domain' );
		?>
		<p>
		<label
			for="<?php echo $this->get_field_id( 'title' ); ?>"><?php _e( 'Title:' ); ?>
		</label>
		<input class="widefat" id="<?php echo $this->get_field_id( 'title' ); ?>"
			name="<?php echo $this->get_field_name( 'title' ); ?>"
			type="text" value="<?php echo esc_attr( $title ); ?>"
		>
		</p>
		<?php
	}

	/**
	 * Sanitize widget form values as they are saved.
	 *
	 * @see WP_Widget::update()
	 *
	 * @param array $new_instance Values just sent to be saved.
	 * @param array $old_instance Previously saved values from database.
	 *
	 * @return array Updated safe values to be saved.
	 */
	public function update( $new_instance, $old_instance ) {
		$instance = array();
		$instance['title'] = ( ! empty( $new_instance['title'] ) )
			? strip_tags( $new_instance['title'] ) : '';

		return $instance;
	}

} // class HSCLib_Data_Management

// Preclude 'headers already sent' error to support wp_redirect()
add_action('init', function(){
	ob_start();
});

// Add the action to register this widget.
// Note: register_widget's first Arg must match widget class name
add_action('widgets_init', function(){
	register_widget('HSCLib_Data_Management');
});
