"""
This module defines a RunGenerator that:
    - is (partially) responsible for validating templates and runs given in a Tate config
    - is responsible for populating arguments, props etc
    - is responsible for generating the specific run's .props file
    - is responsible for giving the right arguments to a benchmark_run.SpecJBBRun so that it can do its thing

The intention is that you pass a Tate Config into the
RunGenerator, and it updates itself to have a list of
all the runs present in that configuration.
"""
from src.validate import TemplateDataSchema, RunConfigSchema


class RunGenerator:
    """
    This class is responsible for taking a Tate config and
    updating self.runs with a list of validated runs that
    you can then pass to benchmark_run.SpecJBBRun for a successful
    benchmarking run.

    The accompanying test module contains examples for how
    this should and shouldn't work.
    """

    def __init__(self, TemplateData=None, RunList=None):
        """
        Initializes this instance to hold all the validated runs in the
        provided configuration.

        :param TemplateData: A TemplateData object. (See src.validate.TemplateDataSchema)
        :param RunList: A list of RunList objects. (See src.validate.RunConfigSchema)
        """
        self.runs = []

        # let's go ahead and populate everything
        for run in RunList:
            run = RunConfigSchema.validate(run)
            template = TemplateData.get(run["template_type"])
            template = TemplateDataSchema.validate(template)

            # populate default_props
            props = template.get("default_props", dict()).copy()
            # populate arguments
            if "translations" in template:
                props.update(
                    {translation: run["args"][arg] for arg, translation in template["translations"].items()})
            if "props_extra" in run:
                props.update(run["props_extra"])

            if "default_props" in template:
                # and let's peek for injector count (specjbb.txi.pergroup.count)
                injectors = template["default_props"].get(
                    "specjbb.txi.pergroups.count", 1)
                # and let's peek for backend count (specjbb.group.count)
                backends = template["default_props"].get(
                    "specjbb.group.count", 1)
            else:
                injectors = 1
                backends = 1

            self.runs.append({
                'controller': {
                    "type": template["run_type"],
                },
                'backends': backends,
                'injectors': injectors,
                'java': template["java"],
                'jar': template["jar"],
                'props': props,
                'props_file': template.get("props_file", 'specjbb2015.props'),
            })
