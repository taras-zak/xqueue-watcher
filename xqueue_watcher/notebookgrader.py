import grader
import imp
import urllib2
import json

class Grader(object):
    def __init__(self):
        self._tests = []
    def input_errors(self, submission_str):
        return []
    def preprocess(self, submission_str):
        return submission_str

    def add_test(self, test):
        self._tests.append(test)

    def tests(self):
        return self._tests


def countTest(title, desctription, string, count, success, fail, weight=1):

    def doit(submission):
        
        actual = submission.count(string)
        passed = 0.0
        result = ''
        if actual < count:
            result = fail
            #tests.append(('Name test', 'description of test', False, string, fail))
        else:
            passed = 1.0 * weight
            result = success
            #tests.append(('Name test', 'description of test', True, string, success))

        return (title, desctription, passed, string, result, weight)
    return doit

def mlTest(title, desctription, string, count, success, fail, weight=1):

    def doit(submission):
        
        actual = submission.count(string)
        passed = 0.0
        result = ''
        if actual < count:
            result = fail
            #tests.append(('Name test', 'description of test', False, string, fail))
        else:
            passed = 1.0 * weight
            result = success
            #tests.append(('Name test', 'description of test', True, string, success))

        return (title, desctription, passed, string, result, weight)
    return doit


class NotebookGrader(grader.Grader):
    def grade(self, grader_path, grader_config, student_response, files):

        results = {
            'errors': [],
            'tests': [],
            'correct': False,
            'score': 0,
        }

        if type(student_response) != unicode:
            self.log.warning("Submission is NOT unicode")

        self.log.warning("Submission: {0}, {1}".format(student_response, len(student_response)))
        self.log.warning("Files: {0}".format(files))

        if files and student_response=='':
            self.log.warning("\nS: {0}\nF: {0}".format(student_response=='', files=={}))
            student_response = urllib2.urlopen(files.values()[0]).read()

        try:
            data = json.loads(student_response)
            cells = data['cells']
            output = [i['outputs'] for i in cells if i.get('outputs')]
            t = []
            for i in output:
                if i[0].get('text'):
                    t.extend(i[0]["text"])
            student_response = ''.join(t)
        except Exception:
            results["errors"].append("Please, attach *.ipynb file")
            self.log.warning('Student attached bad file')
            return results

        #self.log.warning('\nCheck: {0}'.format(student_response))

        grader_module = imp.load_source("grader_module", grader_path)
        grader = grader_module.grader

        self.log.warning('\nTsts: {0}'.format(grader.tests()))
        self.log.warning('\nPath: {0} \nConfig: {1} \nFiles: {2}'.format(grader_path, grader_config, files))

        corrects = []
        weights = 0
        for test in grader.tests():
            (short_desc, long_desc, correct, exp_output, act_output, weight) = test(student_response)
            results['tests'].append((short_desc, long_desc, correct, exp_output, act_output))
            corrects.append(correct)
            weights += weight
            
        #n = len(corrects)
        n = weights
	results['score'] = float(sum(corrects))/n if n > 0 else 0
        results['correct'] = all(corrects) and n > 0
        #results['score'] = float(sum(corrects))/n if n > 0 else 0
        self.log.warning('\nWeight: {0} --- {1} --- {2} --- {3}'.format(corrects, sum(corrects), n, results["score"]))

        return results

