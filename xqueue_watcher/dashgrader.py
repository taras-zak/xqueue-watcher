import random
import urllib2
import imp
from path import path

import jailedgrader
import grader_support
from codejail.jail_code import jail_code


SUPPORT_FILES = [
            path(grader_support.__file__).dirname()
]


class DashGrader(jailedgrader.JailedGrader):
    def run(self, grader_path, tests, grabber, app, seed):
                files = SUPPORT_FILES + [grader_path]
                if self.locale_dir.exists():
                    files.append(self.locale_dir)
                extra_files = [('submission.py', tests.encode('utf-8')), ('grabber.py', grabber.encode('utf-8')), ('flask_app.py', app.encode('utf-8'))]
                argv = ["-m", "grader_support.run", path(grader_path).basename(), 'submission.py', seed]
                #self.log.warning("\nOne: {0}\nFiles: {1}\nExtra: {2}\nArgv: {3}".format(self.codejail_python, files, extra_files, argv))
                r = jail_code(self.codejail_python, files=files, extra_files=extra_files, argv=argv)
                return r

    def grade(self, grader_path, grader_config, submission, files):
               results = {
                   'errors': [],                    
                   'tests': [],                  
                   'correct': False,                   
                   'score': 0,
               }
               #self.log.warning("\nGrader path: {0}\nGrader config: {1}".format(grader_path,grader_config))
               self.log.warning("Files: {0}".format(files))
               seed = str(random.randint(0, 20000))
               app_submission = ''
               #file submission 
               if files and not submission:
                   #self.log.warning("\nS: {0}\nF: {0}".format(submission=='', files=={}))
                   student_response = urllib2.urlopen(files['grabber.py']).read()
                   if 'flask_app.py' in files.keys():
                        app_submission = urllib2.urlopen(files['flask_app.py']).read()
               
               #self.log.warning('\nGrabber: {0},\nApp: {1}'.format(student_response, app_submission))

               tests = path(grader_path).dirname()/grader_config['tests']
               with open(tests) as f:
                   tests = f.read().decode('utf-8')
               
               r = self.run(grader_path, tests, student_response, app_submission, seed)
               self.log.warning("\nOut: {0}\nError:{1}".format(r.stdout,r.stderr))
               
               student_response = r.stdout
               grader_module = imp.load_source("grader_module", grader_path)
               
               grader = grader_module.grader

               
               #self.log.warning('\nTsts: {0}'.format(grader.tests()))
               #self.log.warning('\nPath: {0} \nConfig: {1} \nFiles: {2}'.format(grader_path, grader_config, files))               
               corrects = []               
               weights = 0               
               for test in grader.tests():               
                   (short_desc, long_desc, correct, exp_output, act_output, weight) = test(student_response)                   
                   results['tests'].append((short_desc, long_desc, correct, exp_output, act_output))                   
                   corrects.append(correct)                  
                   weights += weight
               n = weights           
               results['score'] = float(sum(corrects))/n if n > 0 else 0
               results['correct'] = all(corrects) and n > 0                                           
                                                                      
               #self.log.warning('\nWeight: {0} --- {1} --- {2} --- {3}'.format(corrects, sum(corrects), n, results["score"]))
               return results


