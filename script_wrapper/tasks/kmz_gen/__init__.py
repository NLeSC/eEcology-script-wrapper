from script_wrapper.tasks import MatlabTask


class KmzGen(MatlabTask):
    name = 'kmz_gen'
    label = "Generate KMZ file"
    title = """Uses Matlab google earth toolkit"""
    script = 'run_kmz_gen.sh'
    autoregister = False
    matlab_version = '2009b'

    def run(self):
        result = super(KmzGen, self).run()
        return result

    def formfields2taskargs(self, fields, db_url):
        return {}
