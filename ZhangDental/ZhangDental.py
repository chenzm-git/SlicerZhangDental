import base64
import marshal
import os
import sitkUtils
import slicer
import SimpleITK as sitk
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
)

from slicer import vtkMRMLScalarVolumeNode

from medic.access import License


#
# ZhangDental
#


class ZhangDental(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("ZhangDental")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "Examples")]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#ZhangDental">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""")


#
# ZhangDentalParameterNode
#
@parameterNodeWrapper
class ZhangDentalParameterNode:
    """
    The parameters needed by module.
    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """
    inputVolume: vtkMRMLScalarVolumeNode


#
# ZhangDentalWidget
#
class ZhangDentalWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None
        self.loadingWidget = slicer.util.loadUI(self.resourcePath('UI/loading.ui'))
        self.uiWidget = slicer.util.loadUI(self.resourcePath("UI/ZhangDental.ui"))
        self.ui = slicer.util.childWidgetVariables(self.uiWidget)
        self.loadingUi = slicer.util.childWidgetVariables(self.loadingWidget)

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        self.layout.addWidget(self.uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        self.uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = ZhangDentalLogic()

        # Connections
        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        self.ui.applyButton.connect("clicked(bool)", self.onApplyButton)
        self.ui.batchApplyButton.connect("clicked(bool)", self.onBatchApplyButton)

        # Text
        self.ui.cpu_id.text = License.get_cpu_id()

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        pass

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        pass

    def onSceneStartClose(self, caller, event) -> None:
        self.setParameterNode()

    def onSceneEndClose(self, caller, event) -> None:
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        self.setParameterNode()

    def setParameterNode(self) -> None:
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        pass

    def _checkCanApply(self, caller=None, event=None) -> None:
        pass

    def onApplyButton(self) -> None:
        """Run processing when user clicks "Apply" button."""
        with slicer.util.tryWithErrorDisplay(_("Failed to compute results."), waitCursor=True):
            # Compute output
            # self.loadingWidget.show()
            self.logic.process(self.ui.lisence.text, self.ui.model_dir.text, self.ui.inputSelector.currentNode(), callback=self.pop_msg)
            # self.loadingWidget.close()

    def onBatchApplyButton(self) -> None:
        # self.loadingWidget.show()
        self.logic.batch_process(self.ui.lisence.text, self.ui.model_dir.text, self.ui.input_dir.text, self.ui.output_dir.text, callback=self.pop_msg)
        # self.loadingWidget.close()

    def pop_msg(self, prog=None, msg=""):
        print(f'{prog} {msg}', flush=True)
        self.loadingUi.loading_text.text = msg

#
# ZhangDentalLogic
#


class ZhangDentalLogic(ScriptedLoadableModuleLogic):
    def __init__(self) -> None:
        """Called when the logic class is instantiated. Can be used for initializing member variables."""
        ScriptedLoadableModuleLogic.__init__(self)

    def getParameterNode(self):
        return ZhangDentalParameterNode(super().getParameterNode())

    def process(self, sign, model_dir, input_volume: vtkMRMLScalarVolumeNode, callback=None) -> None:
        print("start medic math process!")
        if not os.path.exists(r"./model"):
            os.makedirs(r"./model")
        in_file = r'./model/test.nrrd'
        out_file = r'./model/pred.nrrd'

        input_volume = sitkUtils.PullVolumeFromSlicer(input_volume)
        images = sitk.GetArrayFromImage(input_volume)
        image = sitk.GetImageFromArray(images)
        image.SetSpacing(input_volume.GetSpacing())
        image.SetDirection(input_volume.GetDirection())
        image.SetOrigin(input_volume.GetOrigin())
        sitk.WriteImage(image, in_file)

        if os.path.exists(in_file):
            self.compute_file(sign, model_dir, in_file, out_file)
            if os.path.exists(out_file):
                slicer.util.loadSegmentation(os.getcwd() + out_file)
            else:
                print("no output file!")
        else:
            print("no input file!")
        print("end medicmath process!", flush=True)

    def batch_process(self, sign, model_dir, input_dir, output_dir, callback=None):
        print("start medic batch math process!")
        method = License.get_method("tooth_src")
        if method:
            binary_data = base64.b64decode(method["method"].encode('utf-8'))
            loaded_code = marshal.loads(binary_data)
            # print(dis.dis(loaded_code))
            globals_dict = globals()
            exec(loaded_code, globals_dict)
            try:
                exec_math(sign, input_dir, output_dir, model_dir)
            except NameError:
                print("函数未正确加载或执行。")
        else:
            print(f'no this method')
        print(f"Processing completed")

    def compute_file(self, sign, model_dir, input_file, output_file, callback=None):
        method = License.get_method("tooth_src")
        if method:
            binary_data = base64.b64decode(method["method"].encode('utf-8'))
            loaded_code = marshal.loads(binary_data)
            # print(dis.dis(loaded_code))
            globals_dict = globals()
            exec(loaded_code, globals_dict)
            try:
                # check(sign)
                exec_math_one(sign, input_file, output_file, model_dir)
            except NameError:
                print("函数未正确加载或执行。")
        else:
            print(f'no this method')
        print(f"Processing completed")
