# This file was automatically generated by SWIG (http://www.swig.org).
# Version 1.3.33
#
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _jagpdf
import new
new_instancemethod = new.instancemethod
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'PySwigObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


try:
    import weakref
    weakref_proxy = weakref.proxy
except:
    weakref_proxy = lambda x: x


Exception = _jagpdf.myException

class Document(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Document, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Document, name)
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def __deref__(*args): return _jagpdf.Document___deref__(*args)
    __swig_destroy__ = _jagpdf.delete_Document
    __del__ = lambda self : None;
    def color_space_load(*args): return _jagpdf.Document_color_space_load(*args)
    def page_start(*args): return _jagpdf.Document_page_start(*args)
    def page_end(*args): return _jagpdf.Document_page_end(*args)
    def finalize(*args): return _jagpdf.Document_finalize(*args)
    def page(*args): return _jagpdf.Document_page(*args)
    def page_number(*args): return _jagpdf.Document_page_number(*args)
    def outline(*args): return _jagpdf.Document_outline(*args)
    def font_load(*args): return _jagpdf.Document_font_load(*args)
    def destination_reserve(*args): return _jagpdf.Document_destination_reserve(*args)
    def destination_define_reserved(*args): return _jagpdf.Document_destination_define_reserved(*args)
    def destination_define(*args): return _jagpdf.Document_destination_define(*args)
    def image_definition(*args): return _jagpdf.Document_image_definition(*args)
    def image_load(*args): return _jagpdf.Document_image_load(*args)
    def image_load_file(*args): return _jagpdf.Document_image_load_file(*args)
    def function_2_load(*args): return _jagpdf.Document_function_2_load(*args)
    def function_3_load(*args): return _jagpdf.Document_function_3_load(*args)
    def function_4_load(*args): return _jagpdf.Document_function_4_load(*args)
    def tiling_pattern_load(*args): return _jagpdf.Document_tiling_pattern_load(*args)
    def shading_pattern_load(*args): return _jagpdf.Document_shading_pattern_load(*args)
    def version(*args): return _jagpdf.Document_version(*args)
    def canvas_create(*args): return _jagpdf.Document_canvas_create(*args)
    def define_image_mask(*args): return _jagpdf.Document_define_image_mask(*args)
    def register_image_mask(*args): return _jagpdf.Document_register_image_mask(*args)
Document_swigregister = _jagpdf.Document_swigregister
Document_swigregister(Document)

class ImageMask(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, ImageMask, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, ImageMask, name)
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def __deref__(*args): return _jagpdf.ImageMask___deref__(*args)
    __swig_destroy__ = _jagpdf.delete_ImageMask
    __del__ = lambda self : None;
    def file_name(*args): return _jagpdf.ImageMask_file_name(*args)
    def data(*args): return _jagpdf.ImageMask_data(*args)
    def dimensions(*args): return _jagpdf.ImageMask_dimensions(*args)
    def bit_depth(*args): return _jagpdf.ImageMask_bit_depth(*args)
    def decode(*args): return _jagpdf.ImageMask_decode(*args)
    def interpolate(*args): return _jagpdf.ImageMask_interpolate(*args)
    def matte(*args): return _jagpdf.ImageMask_matte(*args)
ImageMask_swigregister = _jagpdf.ImageMask_swigregister
ImageMask_swigregister(ImageMask)

class Profile(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Profile, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Profile, name)
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def __deref__(*args): return _jagpdf.Profile___deref__(*args)
    __swig_destroy__ = _jagpdf.delete_Profile
    __del__ = lambda self : None;
    def set(*args): return _jagpdf.Profile_set(*args)
    def save_to_file(*args): return _jagpdf.Profile_save_to_file(*args)
Profile_swigregister = _jagpdf.Profile_swigregister
Profile_swigregister(Profile)

LINE_CAP_BUTT = _jagpdf.LINE_CAP_BUTT
LINE_CAP_ROUND = _jagpdf.LINE_CAP_ROUND
LINE_CAP_SQUARE = _jagpdf.LINE_CAP_SQUARE
LINE_JOIN_MITER = _jagpdf.LINE_JOIN_MITER
LINE_JOIN_ROUND = _jagpdf.LINE_JOIN_ROUND
LINE_JOIN_BEVEL = _jagpdf.LINE_JOIN_BEVEL
RI_ABSOLUTE_COLORIMETRIC = _jagpdf.RI_ABSOLUTE_COLORIMETRIC
RI_RELATIVE_COLORIMETRIC = _jagpdf.RI_RELATIVE_COLORIMETRIC
RI_SATURATION = _jagpdf.RI_SATURATION
RI_PERCEPTUAL = _jagpdf.RI_PERCEPTUAL
IMAGE_FORMAT_AUTO = _jagpdf.IMAGE_FORMAT_AUTO
IMAGE_FORMAT_NATIVE = _jagpdf.IMAGE_FORMAT_NATIVE
IMAGE_FORMAT_PNG = _jagpdf.IMAGE_FORMAT_PNG
IMAGE_FORMAT_JPEG = _jagpdf.IMAGE_FORMAT_JPEG
CS_DEVICE_RGB = _jagpdf.CS_DEVICE_RGB
CS_DEVICE_CMYK = _jagpdf.CS_DEVICE_CMYK
CS_DEVICE_GRAY = _jagpdf.CS_DEVICE_GRAY
CS_CIELAB = _jagpdf.CS_CIELAB
CS_CALGRAY = _jagpdf.CS_CALGRAY
CS_CALRGB = _jagpdf.CS_CALRGB
CS_INDEXED = _jagpdf.CS_INDEXED
CS_ICCBASED = _jagpdf.CS_ICCBASED
class StreamOut(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, StreamOut, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, StreamOut, name)
    __repr__ = _swig_repr
    def __init__(self, *args): 
        if self.__class__ == StreamOut:
            args = (None,) + args
        else:
            args = (self,) + args
        this = _jagpdf.new_StreamOut(*args)
        try: self.this.append(this)
        except: self.this = this
    __swig_destroy__ = _jagpdf.delete_StreamOut
    __del__ = lambda self : None;
    def write(*args): return _jagpdf.StreamOut_write(*args)
    def close(*args): return _jagpdf.StreamOut_close(*args)
    def AddRef(*args): return _jagpdf.StreamOut_AddRef(*args)
    def Release(*args): return _jagpdf.StreamOut_Release(*args)
    def check_error(*args): return _jagpdf.StreamOut_check_error(*args)
    def __disown__(self):
        self.this.disown()
        _jagpdf.disown_StreamOut(self)
        return weakref_proxy(self)
StreamOut_swigregister = _jagpdf.StreamOut_swigregister
StreamOut_swigregister(StreamOut)
cvar = _jagpdf.cvar
err_no_error = cvar.err_no_error
err_invalid_operation = cvar.err_invalid_operation
err_io_error = cvar.err_io_error
err_internal_error = cvar.err_internal_error
err_invalid_input = cvar.err_invalid_input
err_invalid_value = cvar.err_invalid_value
err_operation_failed = cvar.err_operation_failed

class Page(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Page, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Page, name)
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def annotation_uri(*args): return _jagpdf.Page_annotation_uri(*args)
    def annotation_goto(*args): return _jagpdf.Page_annotation_goto(*args)
    def canvas(*args): return _jagpdf.Page_canvas(*args)
Page_swigregister = _jagpdf.Page_swigregister
Page_swigregister(Page)

class Canvas(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Canvas, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Canvas, name)
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def state_save(*args): return _jagpdf.Canvas_state_save(*args)
    def state_restore(*args): return _jagpdf.Canvas_state_restore(*args)
    def transform(*args): return _jagpdf.Canvas_transform(*args)
    def translate(*args): return _jagpdf.Canvas_translate(*args)
    def scale(*args): return _jagpdf.Canvas_scale(*args)
    def rotate(*args): return _jagpdf.Canvas_rotate(*args)
    def skew(*args): return _jagpdf.Canvas_skew(*args)
    def line_width(*args): return _jagpdf.Canvas_line_width(*args)
    def line_dash(*args): return _jagpdf.Canvas_line_dash(*args)
    def line_miter_limit(*args): return _jagpdf.Canvas_line_miter_limit(*args)
    def line_cap(*args): return _jagpdf.Canvas_line_cap(*args)
    def line_join(*args): return _jagpdf.Canvas_line_join(*args)
    def move_to(*args): return _jagpdf.Canvas_move_to(*args)
    def line_to(*args): return _jagpdf.Canvas_line_to(*args)
    def rectangle(*args): return _jagpdf.Canvas_rectangle(*args)
    def circle(*args): return _jagpdf.Canvas_circle(*args)
    def bezier_to(*args): return _jagpdf.Canvas_bezier_to(*args)
    def bezier_to_2nd_ctrlpt(*args): return _jagpdf.Canvas_bezier_to_2nd_ctrlpt(*args)
    def bezier_to_1st_ctrlpt(*args): return _jagpdf.Canvas_bezier_to_1st_ctrlpt(*args)
    def arc(*args): return _jagpdf.Canvas_arc(*args)
    def arc_to(*args): return _jagpdf.Canvas_arc_to(*args)
    def path_close(*args): return _jagpdf.Canvas_path_close(*args)
    def path_paint(*args): return _jagpdf.Canvas_path_paint(*args)
    def alpha(*args): return _jagpdf.Canvas_alpha(*args)
    def color_space(*args): return _jagpdf.Canvas_color_space(*args)
    def color(*args): return _jagpdf.Canvas_color(*args)
    def image(*args): return _jagpdf.Canvas_image(*args)
    def color_space_pattern(*args): return _jagpdf.Canvas_color_space_pattern(*args)
    def color_space_pattern_uncolored(*args): return _jagpdf.Canvas_color_space_pattern_uncolored(*args)
    def pattern(*args): return _jagpdf.Canvas_pattern(*args)
    def shading_apply(*args): return _jagpdf.Canvas_shading_apply(*args)
    def text_font(*args): return _jagpdf.Canvas_text_font(*args)
    def text_character_spacing(*args): return _jagpdf.Canvas_text_character_spacing(*args)
    def text_horizontal_scaling(*args): return _jagpdf.Canvas_text_horizontal_scaling(*args)
    def text_rendering_mode(*args): return _jagpdf.Canvas_text_rendering_mode(*args)
    def text_rise(*args): return _jagpdf.Canvas_text_rise(*args)
    def text_start(*args): return _jagpdf.Canvas_text_start(*args)
    def text_end(*args): return _jagpdf.Canvas_text_end(*args)
    def text(*args): return _jagpdf.Canvas_text(*args)
    def text_glyphs(*args): return _jagpdf.Canvas_text_glyphs(*args)
    def text_translate_line(*args): return _jagpdf.Canvas_text_translate_line(*args)
    __swig_destroy__ = _jagpdf.delete_Canvas
    __del__ = lambda self : None;
    def scaled_image(*args): return _jagpdf.Canvas_scaled_image(*args)
    def alpha_is_shape(*args): return _jagpdf.Canvas_alpha_is_shape(*args)
Canvas_swigregister = _jagpdf.Canvas_swigregister
Canvas_swigregister(Canvas)

class DocumentOutline(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, DocumentOutline, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, DocumentOutline, name)
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def item(*args): return _jagpdf.DocumentOutline_item(*args)
    def level_down(*args): return _jagpdf.DocumentOutline_level_down(*args)
    def level_up(*args): return _jagpdf.DocumentOutline_level_up(*args)
    def color(*args): return _jagpdf.DocumentOutline_color(*args)
    def style(*args): return _jagpdf.DocumentOutline_style(*args)
    def state_save(*args): return _jagpdf.DocumentOutline_state_save(*args)
    def state_restore(*args): return _jagpdf.DocumentOutline_state_restore(*args)
DocumentOutline_swigregister = _jagpdf.DocumentOutline_swigregister
DocumentOutline_swigregister(DocumentOutline)

class Font(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Font, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Font, name)
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def is_bold(*args): return _jagpdf.Font_is_bold(*args)
    def is_italic(*args): return _jagpdf.Font_is_italic(*args)
    def size(*args): return _jagpdf.Font_size(*args)
    def family_name(*args): return _jagpdf.Font_family_name(*args)
    def advance(*args): return _jagpdf.Font_advance(*args)
    def glyph_width(*args): return _jagpdf.Font_glyph_width(*args)
    def height(*args): return _jagpdf.Font_height(*args)
    def ascender(*args): return _jagpdf.Font_ascender(*args)
    def descender(*args): return _jagpdf.Font_descender(*args)
    def bbox_xmin(*args): return _jagpdf.Font_bbox_xmin(*args)
    def bbox_ymin(*args): return _jagpdf.Font_bbox_ymin(*args)
    def bbox_xmax(*args): return _jagpdf.Font_bbox_xmax(*args)
    def bbox_ymax(*args): return _jagpdf.Font_bbox_ymax(*args)
Font_swigregister = _jagpdf.Font_swigregister
Font_swigregister(Font)

class ImageDef(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, ImageDef, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, ImageDef, name)
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def file_name(*args): return _jagpdf.ImageDef_file_name(*args)
    def data(*args): return _jagpdf.ImageDef_data(*args)
    def dimensions(*args): return _jagpdf.ImageDef_dimensions(*args)
    def color_space(*args): return _jagpdf.ImageDef_color_space(*args)
    def bits_per_component(*args): return _jagpdf.ImageDef_bits_per_component(*args)
    def format(*args): return _jagpdf.ImageDef_format(*args)
    def dpi(*args): return _jagpdf.ImageDef_dpi(*args)
    def interpolate(*args): return _jagpdf.ImageDef_interpolate(*args)
    def decode(*args): return _jagpdf.ImageDef_decode(*args)
    def color_key_mask(*args): return _jagpdf.ImageDef_color_key_mask(*args)
    def gamma(*args): return _jagpdf.ImageDef_gamma(*args)
    def alternate_for_printing(*args): return _jagpdf.ImageDef_alternate_for_printing(*args)
    def image_mask(*args): return _jagpdf.ImageDef_image_mask(*args)
    def rendering_intent(*args): return _jagpdf.ImageDef_rendering_intent(*args)
ImageDef_swigregister = _jagpdf.ImageDef_swigregister
ImageDef_swigregister(ImageDef)

class Image(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, Image, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, Image, name)
    def __init__(self): raise AttributeError, "No constructor defined"
    __repr__ = _swig_repr
    def width(*args): return _jagpdf.Image_width(*args)
    def height(*args): return _jagpdf.Image_height(*args)
    def bits_per_component(*args): return _jagpdf.Image_bits_per_component(*args)
    def dpi_x(*args): return _jagpdf.Image_dpi_x(*args)
    def dpi_y(*args): return _jagpdf.Image_dpi_y(*args)
Image_swigregister = _jagpdf.Image_swigregister
Image_swigregister(Image)

create_profile = _jagpdf.create_profile
create_profile_from_string = _jagpdf.create_profile_from_string
create_profile_from_file = _jagpdf.create_profile_from_file
version = _jagpdf.version
intrusive_ptr_add_ref = _jagpdf.intrusive_ptr_add_ref
intrusive_ptr_release = _jagpdf.intrusive_ptr_release

create_file = _jagpdf.create_file
create_stream = _jagpdf.create_stream

