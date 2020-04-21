#version 100
#extension GL_ARB_explicit_attrib_location : require
precision mediump float;

uniform sampler2D tex;
uniform int using_textures;
varying vec2 texcoord;
varying vec4 colour;

//varying vec4 out_colour;

void main()
{
    if(1 == using_textures) {
        gl_FragColor = texture2D(tex, texcoord)*colour;
    }
    else {
        gl_FragColor = colour;
    }
    if(gl_FragColor.a == 0.0) {
        discard;
    }
}
