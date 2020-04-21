#version 120

uniform vec3 screen_dimensions;
uniform vec2 translation;
uniform vec2 scale;
attribute vec3 vertex_data;
attribute vec2 tc_data;
attribute vec4 colour_data;

varying out vec2 texcoord;
varying out vec4 colour;

void main()
{
    gl_Position = vec4( (((vertex_data.x+translation.x)*2*scale.x)/screen_dimensions.x)-1,
                        (((vertex_data.y+translation.y)*2*scale.y)/screen_dimensions.y)-1,
                        -vertex_data.z/screen_dimensions.z,
                        1.0) ;
    texcoord    = tc_data;
    colour      = colour_data;
}
