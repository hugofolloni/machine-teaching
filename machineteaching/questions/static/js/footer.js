function showBox() {
	$('body').append('<div class="bg2"></div>');
	$('.bg2').append('<div class="card"></div>');
	$('.bg2 .card').append(`<h3></h3>
		<span>
		  <a class="link" onclick="hideBox()">${close}</a>
		</span>
		<div class="popup-content"></div>`);
};

function hideBox() {
	$('.bg2').remove();
}

function showConditions(language) {
	if (language == "en") {
    	var title = "Terms and conditions"
    	var content = `Last updated: August 29, 2020
                <br><br>
                <h4>PRIVACY</h4>
                <ul>
                    <li>
                        We have established a Privacy Policy, which is considered
                        part of our Terms of Service. Please read the Privacy Policy to
                        understand our commitment to the privacy of our users.  
                    </li>
                    <li>
                        By registering, the user agrees that all the data
                        provided to the website may be used as anonymous data research
                        intended to enhance the Machine Teaching Platform as well as the
                        quality of learning and related sciences worldwide.
                    </li>
                </ul>
                <h4>YOUR ACCOUNT</h4>
                <ul>
                    <li>
                        When and if you register with the Site, you agree to (a) provide
                        accurate, current and complete information about yourself as
                        prompted by our registration form (including your email address),
                        (b) allow the Machine Teaching Platform to conduct A/B testing
                        using information gathered from the actions that you take with your
                        account, and maintain and update your information (including
                        your email address) to keep it accurate, current and complete. You
                        acknowledge that, if any information provided by you is untrue,
                        inaccurate, not current or incomplete, we reserve the right to
                        terminate this Agreement and your access to the Site. As part of
                        the registration process, you will be asked to select a username
                        and password. We may refuse to grant you a username that
                        impersonates someone else, is or may be illegal, is or may be
                        protected by trademark or other proprietary rights law, is vulgar
                        or otherwise offensive, or may cause confusion, as determined by us
                        in our sole discretion. You will be responsible for the
                        confidentiality and use of your username and password and agree not
                        to transfer or resell your use of or access to the Site to any
                        third party. If you have reason to believe that your account with
                        us is no longer secure, you must promptly change your password. YOU
                        ARE ENTIRELY RESPONSIBLE FOR MAINTAINING THE CONFIDENTIALITY OF
                        YOUR USERNAME AND PASSWORD AND FOR ANY AND ALL ACTIVITIES THAT ARE
                        CONDUCTED THROUGH YOUR ACCOUNT.  
                    </li>
                </ul>
                <h4>DISCLAIMERS</h4>
                <ul>
                    <li>
                       The Machine Teaching developers have worked hard to develop services
                       and materials on this Site that assist students, educators, parents,
                       and guardians in the
                       learning process. Nonetheless, THE SITE, THE MATERIALS ON THE SITE,
                       AND ANY PRODUCT OR SERVICE OBTAINED THROUGH THE SITE ARE PROVIDED
                       "AS IS" AND WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
                       IMPLIED, INCLUDING, WITHOUT LIMITATION, IMPLIED WARRANTIES OF TITLE,
                       NON-INFRINGEMENT, ACCURACY, MERCHANTABILITY, AND FITNESS FOR A
                       PARTICULAR PURPOSE, AND ANY WARRANTIES THAT MAY ARISE FROM COURSE OF
                       DEALING, COURSE OF PERFORMANCE OR USAGE OF TRADE. Specifically and
                       without limitation, THE PLATFORM AND ITS AFFILIATES, LICENSORS, SUPPLIERS,
                       SPONSORS AND AGENTS DO NOT WARRANT THE SERVICES ON THIS SITE WILL BE
                       UNINTERRUPTED, SECURE, OR ERROR-FREE; THAT THE SITE IS FREE OF
                       VIRUSES OR OTHER HARMFUL COMPONENTS; THAT THE CONTENT ON THE SITE IS
                       ENTIRELY CORRECT, ACCURATE, UP-TO-DATE, OR RELIABLE; THAT DEFECTS
                       WILL BE CORRECTED, OR THAT THE SITE, THE SERVER(S) ON WHICH THE SITE
                       IS HOSTED OR SOFTWARE ARE FREE OF VIRUSES OR OTHER HARMFUL
                       COMPONENTS. ANY MATERIAL DOWNLOADED OR OTHERWISE OBTAINED THROUGH
                       THE USE OF THE SERVICE IS DONE AT YOUR OWN DISCRETION AND RISK AND
                       THAT YOU WILL BE SOLELY RESPONSIBLE FOR ANY DAMAGE TO YOUR COMPUTER
                       SYSTEM OR LOSS OF DATA THAT RESULTS FROM THE DOWNLOAD OF ANY SUCH
                       MATERIAL. YOUR USE OF THE SITE AND ANY MATERIALS PROVIDED THROUGH
                       THE SITE IS ENTIRELY AT YOUR OWN RISK.
                    </li>
                </ul>
                <h4>CONTACT INFORMATION</h4>
                <ul>
                    <li>
                       If you have any questions or concerns about this 
                       Terms and Conditions,
                       please contact us at:
                       laura.moraes@coppe.ufrj.br.
                    </li>
                </ul>`}
    else {
    	var title = "Termos e condições"
    	var content = `Última atualização: 29 de Agosto de 2020
                <br><br>
                <h4>PRIVACIDADE</h4>
                <ul>
                    <li>
                        Estabelecemos uma Política de Privacidade, que é considerada parte de
                        nossos Termos de Serviço. Leia a Política de Privacidade para entender
                        nosso compromisso com a privacidade de nossos usuários.
                    </li>
                    <li>
                        Ao se cadastrar, o usuário concorda que todos os dados fornecidos ao site
                        podem ser usados nesta pesquisa como dados anônimos com o objetivo de 
                        aprimorar a Plataforma Machine Teaching, bem como a qualidade do aprendizado
                        e ciências afins em todo o mundo.
                    </li>
                </ul>
                <h4>SUA CONTA</h4>
                <ul>
                    <li>
                        When and if you register with the Site, you agree to (a) provide
                        accurate, current and complete information about yourself as
                        prompted by our registration form (including your email address),
                        (b) allow the Machine Teaching Platform to conduct A/B testing
                        using information gathered from the actions that you take with your
                        account, and maintain and update your information (including
                        your email address) to keep it accurate, current and complete. You
                        acknowledge that, if any information provided by you is untrue,
                        inaccurate, not current or incomplete, we reserve the right to
                        terminate this Agreement and your access to the Site. As part of
                        the registration process, you will be asked to select a username
                        and password. We may refuse to grant you a username that
                        impersonates someone else, is or may be illegal, is or may be
                        protected by trademark or other proprietary rights law, is vulgar
                        or otherwise offensive, or may cause confusion, as determined by us
                        in our sole discretion. You will be responsible for the
                        confidentiality and use of your username and password and agree not
                        to transfer or resell your use of or access to the Site to any
                        third party. If you have reason to believe that your account with
                        us is no longer secure, you must promptly change your password. YOU
                        ARE ENTIRELY RESPONSIBLE FOR MAINTAINING THE CONFIDENTIALITY OF
                        YOUR USERNAME AND PASSWORD AND FOR ANY AND ALL ACTIVITIES THAT ARE
                        CONDUCTED THROUGH YOUR ACCOUNT.  
                    </li>
                </ul>
                <h4>TERMO DE RESPONSABILIDADE</h4>
                <ul>
                    <li>
                       The Machine Teaching developers have worked hard to develop services
                       and materials on this Site that assist students, educators, parents,
                       and guardians in the
                       learning process. Nonetheless, THE SITE, THE MATERIALS ON THE SITE,
                       AND ANY PRODUCT OR SERVICE OBTAINED THROUGH THE SITE ARE PROVIDED
                       "AS IS" AND WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
                       IMPLIED, INCLUDING, WITHOUT LIMITATION, IMPLIED WARRANTIES OF TITLE,
                       NON-INFRINGEMENT, ACCURACY, MERCHANTABILITY, AND FITNESS FOR A
                       PARTICULAR PURPOSE, AND ANY WARRANTIES THAT MAY ARISE FROM COURSE OF
                       DEALING, COURSE OF PERFORMANCE OR USAGE OF TRADE. Specifically and
                       without limitation, THE PLATFORM AND ITS AFFILIATES, LICENSORS, SUPPLIERS,
                       SPONSORS AND AGENTS DO NOT WARRANT THE SERVICES ON THIS SITE WILL BE
                       UNINTERRUPTED, SECURE, OR ERROR-FREE; THAT THE SITE IS FREE OF
                       VIRUSES OR OTHER HARMFUL COMPONENTS; THAT THE CONTENT ON THE SITE IS
                       ENTIRELY CORRECT, ACCURATE, UP-TO-DATE, OR RELIABLE; THAT DEFECTS
                       WILL BE CORRECTED, OR THAT THE SITE, THE SERVER(S) ON WHICH THE SITE
                       IS HOSTED OR SOFTWARE ARE FREE OF VIRUSES OR OTHER HARMFUL
                       COMPONENTS. ANY MATERIAL DOWNLOADED OR OTHERWISE OBTAINED THROUGH
                       THE USE OF THE SERVICE IS DONE AT YOUR OWN DISCRETION AND RISK AND
                       THAT YOU WILL BE SOLELY RESPONSIBLE FOR ANY DAMAGE TO YOUR COMPUTER
                       SYSTEM OR LOSS OF DATA THAT RESULTS FROM THE DOWNLOAD OF ANY SUCH
                       MATERIAL. YOUR USE OF THE SITE AND ANY MATERIALS PROVIDED THROUGH
                       THE SITE IS ENTIRELY AT YOUR OWN RISK.
                    </li>
                 </ul>
                <h4>CONTATO</h4>
                <ul>
                    <li>
                       Se você ainda possui alguma dúvida ou preocupações sobre este
                       Termos e Condições,
                       contate-nos em:
                       laura.moraes@coppe.ufrj.br.
                    </li>
                </ul>`}

	showBox()
	$('.bg2 .card h3').append(title);
	$('.bg2 .card div').append(content);
};

function showPrivacy(language) {
	if (language == "en") {
    	var title = "Privacy policy"
    	var content = `Last updated: August 29, 2020
            <br><br>
            <h4>COMMERCIAL USE </h4>
            <ul>
                <li>
                   
                   Machine Teaching will never use our Platform for commercial use. We
                   will never advertise on our site.  Additionally, we will never sell
                   personally identifiable or non-personally identifiable information
                   to third parties.  
                   
                </li>
                <li>
                   
                    If you wish to become a Registered User (Student User or Teacher
                    User) of the Platform, you must provide us with certain information
                    as part of the registration process. In this Privacy Policy, when
                    we use the term "Personally Identifiable Information", we mean any
                    information that can be used to identify or contact a specific
                    individual. We use Personally Identifiable Information to process
                    requests made through this Site and Platform, such as registration
                    requests. The user name that is assigned to you during the
                    registration process will identify you on the Platform in
                    conjunction with content that you submit to the Platform, and this
                    information may be viewed by Users. All passwords are salted before
                    being stored, so we are not aware of the passwords of any users.
                   
                </li>
                <li>
                    
                   Personally Identifiable Information and other data that you
                   furnished through the Platform may remain in our records even if you
                   are no longer a User and can be used by us in accordance with this
                   Privacy Policy.  
                   
                </li>
                <li>
                    
                   We may collect certain information automatically when you visit the
                   Platform or Site, such as the browser you are using, the Internet
                   address from which you linked to the Platform or Site, the operating
                   system of your computer, the unique IP address of the computer you
                   used to access the Platform or Site and usage and browsing habits.
                   We use this information to administer and improve your experience on
                   the Platform and Site, to help diagnose and troubleshoot potential
                   server malfunctions, and to gather broad demographic information. If
                   a Student User enters a class code provided by a Teacher User, then
                   the Teacher User may view information about that student.  
                   
                </li>
                <li>
                    
                    To help make sure you receive information that is relevant to you,
                    the Platform uses data "cookies." These cookies are small data
                    files stored on your computer that identify you as a previous
                    visitor to the Platform and help us to personalize your experience
                    when you arrive. Most web browsers are set to accept cookies. You
                    can instruct your browser not to accept cookies. However, if you
                    disable this function, you will not be able to use some of the
                    features on the Platform.
                   
                </li>
                <li>
                    
                   We work with third parties who provide services such as data
                   analysis (for example we may use Google Analytics), infrastructure
                   provision (for example we use Microsoft Azure), IT services (for
                   example we may use Cloudfare to prevent denial of service attacks),
                   email delivery services (for example we may use MailChimp to communicate
                   with non-student stakeholders), and other similar services. We may
                   share Personally Identifiable Information about account holders with
                   these parties solely for the purpose of enabling them to provide
                   these services. We only share with those that have privacy policies
                   entirely consistent with our privacy policy.
                   
                </li>
                <li>
                    
                   We may use Personally Identifiable Information about you for
                   internal purposes, including without limitation data analysis and
                   audits. If you are a Student User, your respective Teacher User may
                   also choose to share related information that they might find useful
                   to the research, such as exams and assignments grades taken
                   offline and outside the Platform.  
                   
                </li>
                <li>
                    
                   Notwithstanding any other provision of this Policy to the contrary,
                   we reserve the right to disclose your Personally Identifiable
                   Information to others as we believe to be appropriate (a) under
                   applicable law; (b) to comply with legal process (c) to respond to
                   governmental requests; (d) to enforce our Terms of Service; (e) to
                   protect our operations; (f) to protect the rights, privacy, safety
                   or property of you or others; and (g) to permit us to pursue
                   available remedies or limit the damages that we may sustain. For
                   example, we may, to the fullest extent the law allows, disclose
                   Personally Identifiable Information about you to law enforcement
                   agencies to assist them in identifying individuals who have been or
                   may be engaged in unlawful activities.  
                   
                </li>
            </ul>
            <h4>NON-PERSONALLY IDENTIFIABLE INFORMATION</h4>
            <ul>
                <li>
                    
                    Non-Personally Identifiable Information is aggregated information,
                    demographic information, and other information that does not reveal
                    a person’s specific identity. We may collect Non-Personally
                    Identifiable Information (e.g., interests, geographic location, zip
                    codes, etc.) when you voluntarily provide such information to us,
                    such as through survey responses. Such information constitutes
                    Non-Personally Identifiable Information because, unless combined
                    with your name or other Personally Identifiable Information, it
                    does not personally identify you or any other user. We retain
                    aggregated student data exclusively for the educational purpose of
                    improving the Machine Teaching Platform.
                   
                </li>
                <li>
                    
                    Additionally, we may aggregate Personally Identifiable Information
                    in a manner such that the end product does not personally identify
                    you or any other user of the Platform or Site. For example, we
                    might use Personally Identifiable Information to calculate the
                    percentage of our Users who have a particular zip code. Such
                    aggregate information is considered Non-Personally Identifiable
                    Information for purposes of this Policy. Because Non-Personally
                    Identifiable Information does not personally identify you, we may
                    use or disclose such information for any purpose. Upon request,
                    user names and birthdates will be removed leaving only
                    ‘non-personally identifiable information”.  Student generated
                    content, other than answers to test questions, will also be
                    destroyed.
                   
                </li>
            </ul>
            <h4>DATA SECURITY AND BREACH INCIDENT RESPONSE PLAN</h4>
            <ul>
                <li>
                    
                    We have implemented software and hardware security measures
                    intended to protect your Personally Identifiable Information from
                    unauthorized access. Although we strive to protect
                    your information, we cannot ensure or warrant the security of any
                    information you transmit to us through or in connection with the
                    Platform. Despite our precautions, no system can completely protect
                    against unauthorized access to your Personally Identifiable
                    Information, and your use of the Platform indicates that you are
                    willing to assume this risk. If you have reason to believe that
                    your interaction with us is no longer secure, you must immediately
                    notify us of the problem by contacting us.
                   
                </li>
            </ul>
            <h4>CONTACT INFORMATION</h4>
            <ul>
                <li>
                   If you have any questions or concerns about this 
                   Privacy Policy,
                   please contact us at: 
                   laura.moraes@coppe.ufrj.br.       
                </li>
            </ul>`
    }
    else {
        var title = "Política de privacidade"
        var content = `Última atualização: 29 de Agosto de 2020
            <br><br>
            <h4>COMMERCIAL USE </h4>
            <ul>
                <li>
                   
                   Machine Teaching will never use our Platform for commercial use. We
                   will never advertise on our site.  Additionally, we will never sell
                   personally identifiable or non-personally identifiable information
                   to third parties.  
                   
                </li>
                <li>
                   
                    If you wish to become a Registered User (Student User or Teacher
                    User) of the Platform, you must provide us with certain information
                    as part of the registration process. In this Privacy Policy, when
                    we use the term "Personally Identifiable Information", we mean any
                    information that can be used to identify or contact a specific
                    individual. We use Personally Identifiable Information to process
                    requests made through this Site and Platform, such as registration
                    requests. The user name that is assigned to you during the
                    registration process will identify you on the Platform in
                    conjunction with content that you submit to the Platform, and this
                    information may be viewed by Users. All passwords are salted before
                    being stored, so we are not aware of the passwords of any users.
                   
                </li>
                <li>
                    
                   Personally Identifiable Information and other data that you
                   furnished through the Platform may remain in our records even if you
                   are no longer a User and can be used by us in accordance with this
                   Privacy Policy.  
                   
                </li>
                <li>
                    
                   We may collect certain information automatically when you visit the
                   Platform or Site, such as the browser you are using, the Internet
                   address from which you linked to the Platform or Site, the operating
                   system of your computer, the unique IP address of the computer you
                   used to access the Platform or Site and usage and browsing habits.
                   We use this information to administer and improve your experience on
                   the Platform and Site, to help diagnose and troubleshoot potential
                   server malfunctions, and to gather broad demographic information. If
                   a Student User enters a class code provided by a Teacher User, then
                   the Teacher User may view information about that student.  
                   
                </li>
                <li>
                    
                    To help make sure you receive information that is relevant to you,
                    the Platform uses data "cookies." These cookies are small data
                    files stored on your computer that identify you as a previous
                    visitor to the Platform and help us to personalize your experience
                    when you arrive. Most web browsers are set to accept cookies. You
                    can instruct your browser not to accept cookies. However, if you
                    disable this function, you will not be able to use some of the
                    features on the Platform.
                   
                </li>
                <li>
                    
                   We work with third parties who provide services such as data
                   analysis (for example we may use Google Analytics), infrastructure
                   provision (for example we use Microsoft Azure), IT services (for
                   example we may use Cloudfare to prevent denial of service attacks),
                   email delivery services (for example we may use MailChimp to communicate
                   with non-student stakeholders), and other similar services. We may
                   share Personally Identifiable Information about account holders with
                   these parties solely for the purpose of enabling them to provide
                   these services. We only share with those that have privacy policies
                   entirely consistent with our privacy policy.
                   
                </li>
                <li>
                    
                   We may use Personally Identifiable Information about you for
                   internal purposes, including without limitation data analysis and
                   audits. If you are a Student User, your respective Teacher User may
                   also choose to share related information that they might find useful
                   to the research, such as exams and assignments grades taken
                   offline and outside the Platform.  
                   
                </li>
                <li>
                    
                   Notwithstanding any other provision of this Policy to the contrary,
                   we reserve the right to disclose your Personally Identifiable
                   Information to others as we believe to be appropriate (a) under
                   applicable law; (b) to comply with legal process (c) to respond to
                   governmental requests; (d) to enforce our Terms of Service; (e) to
                   protect our operations; (f) to protect the rights, privacy, safety
                   or property of you or others; and (g) to permit us to pursue
                   available remedies or limit the damages that we may sustain. For
                   example, we may, to the fullest extent the law allows, disclose
                   Personally Identifiable Information about you to law enforcement
                   agencies to assist them in identifying individuals who have been or
                   may be engaged in unlawful activities.  
                   
                </li>
            </ul>
            <h4>NON-PERSONALLY IDENTIFIABLE INFORMATION</h4>
            <ul>
                <li>
                    
                    Non-Personally Identifiable Information is aggregated information,
                    demographic information, and other information that does not reveal
                    a person’s specific identity. We may collect Non-Personally
                    Identifiable Information (e.g., interests, geographic location, zip
                    codes, etc.) when you voluntarily provide such information to us,
                    such as through survey responses. Such information constitutes
                    Non-Personally Identifiable Information because, unless combined
                    with your name or other Personally Identifiable Information, it
                    does not personally identify you or any other user. We retain
                    aggregated student data exclusively for the educational purpose of
                    improving the Machine Teaching Platform.
                   
                </li>
                <li>
                    
                    Additionally, we may aggregate Personally Identifiable Information
                    in a manner such that the end product does not personally identify
                    you or any other user of the Platform or Site. For example, we
                    might use Personally Identifiable Information to calculate the
                    percentage of our Users who have a particular zip code. Such
                    aggregate information is considered Non-Personally Identifiable
                    Information for purposes of this Policy. Because Non-Personally
                    Identifiable Information does not personally identify you, we may
                    use or disclose such information for any purpose. Upon request,
                    user names and birthdates will be removed leaving only
                    ‘non-personally identifiable information”.  Student generated
                    content, other than answers to test questions, will also be
                    destroyed.
                   
                </li>
            </ul>
            <h4>DATA SECURITY AND BREACH INCIDENT RESPONSE PLAN</h4>
            <ul>
                <li>
                    
                    We have implemented software and hardware security measures
                    intended to protect your Personally Identifiable Information from
                    unauthorized access. Although we strive to protect
                    your information, we cannot ensure or warrant the security of any
                    information you transmit to us through or in connection with the
                    Platform. Despite our precautions, no system can completely protect
                    against unauthorized access to your Personally Identifiable
                    Information, and your use of the Platform indicates that you are
                    willing to assume this risk. If you have reason to believe that
                    your interaction with us is no longer secure, you must immediately
                    notify us of the problem by contacting us.
                   
                </li>
            </ul>
            <h4>CONTACT INFORMATION</h4>
            <ul>
                <li>
                   Se você ainda possui alguma dúvida ou preocupações sobre este 
                   Política de Privacidade,
                   contate-nos em:
                   laura.moraes@coppe.ufrj.br.
                </li>
            </ul>`
    }

	showBox()
	$('.bg2 .card h3').append(title);
	$('.bg2 .card div').append(content);
};

var logos = `<div class="logos">
             <a href="http://ufrj.br/">
             <img src="${ufrj}"></a>
             <a href="http://cnpq.br/">
             <img src="${cnpq}"></a>
             <a href="http://faperj.br/">
             <img src="${faperj}"></a>
             <br>
             <a href="http://dcc.ufrj.br/">
             <img src="${dcc}"></a>
             <a href="http://coppe.ufrj.br/">
             <img src="${coppe}"></a>
             <a href="http://cos.ufrj.br/">
             <img src="${pesc}"></a>
             <br><br></div>`


function showAbout(language) {
	if (language == "en") {
    	var title = "About this research"
    	var content = `<p class="research">It is important to understand why students succeed or fail when taking a
                course so we can <span class="highlight">improve teaching methods</span> by identifying students\' needs
            and to <span class="highlight">provide personalized education</span>. Smart learning content is defined as
        visualizations, simulations and web-based environments that provide outputs
        for students based on the students\' input [1]. The adoption of smart
        learning content in classrooms and in self-learning environments <span class="highlight">motivates
        students [2]–[5], improves student learning, decreases student dropout or
        failure [2], [6]–[8] while increasing their self-confidence, especially in
        female students [6].</span>
            </p>
            <p class="research">Also, Python is a general-purpose language, which means it can be used in a
        large variety of projects. This can be great to stimulate students, since they
        can work in projects they actually relate to. Python is also user-friendly and
        for the past seven years, it has been the fastest-growing major programming
        language [9], <span class="highlight">being correlated with trending careers, such as DevOps and Data
            Scientist [10]</span>. According to the 2015 review [8], only 11&#37; of the Educational
        Data Mining and Learning Analytics papers about programming courses reported
        using Python as the course language. However, this is changing. A 2017 review
        on the Introductory Programming courses in Australasia universities [11]
        reported a shift from Java to Python in the past years and the 2018 review on
        Introductory Programming literature [12] already presents a higher number of
        papers using Python as the course language. Nonetheless, even though we already
        have different tools to support online learning, it is still hard to find open
        datasets containing student submissions for Python problems and related
        information that can be important to get a better insight on students\'
        knowledge.</p>
            <p class="research">These factors motivate our objective: the creation, deployment and use of
        online intelligent systems in Introduction to Programming classes using the
        Python language as a way to <span class="highlight">uncover students’ difficulties, to understand their
            knowledge and to provide timely feedback to keep students engaged.</span>
            </p>
            Interested? Take a look at 
            <a class="highlight" target="_blank"
            href="https://drive.google.com/file/d/1SqqBEAIjiOaGY3Ajdp9tPmsw7Dc-N8Ly/view">
            our paper</a>.</div>
        <p>References:<br>
        [1]    P. Brusilovsky et al., “Increasing Adoption of Smart Learning Content for Computer Science Education,” 2014, doi: 10.1145/2713609.2713611.<br>
        [2]    L. Benotti, M. J. Gomez, F. Aloi, and F. Bulgarelli, “The effect of a web-based coding tool with automatic feedback on students’ performance and perceptions,” SIGCSE 2018 - Proceedings of the 49th ACM Technical Symposium on Computer Science Education. 2018.<br>
        [3]    I. Jivet, M. Scheffel, M. Specht, and H. Drachsler, “License to evaluate: Preparing learning analytics dashboards for educational practice,” ACM International Conference Proceeding Series. 2018.<br>
        [4]    A. Latham, K. Crockett, D. McLean, and B. Edmonds, “A conversational intelligent tutoring system to automatically predict learning styles,” Computers and Education, vol. 59, no. 1, pp. 95–109, 2012, doi: 10.1016/j.compedu.2011.11.001.<br>
        [5]    R. Lobb and J. Harlow, “Coderunner: A tool for assessing computer programming skills,” ACM Inroads, 2016, doi: 10.1145/2810041.<br>
        [6]    A. N. Kumar, “The effect of using problem-solving software tutors on the self-confidence of female students,” ACM SIGCSE Bulletin, 2008, doi: 10.1145/1352322.1352309.<br>
        [7]    E. Johns, O. M. Aodha, and G. J. Brostow, “Becoming the expert - Interactive multi-class machine teaching,” in Proceedings of the IEEE Computer Society Conference on Computer Vision and Pattern Recognition, 2015, vol. 07-12-June, pp. 2616–2624, doi: 10.1109/CVPR.2015.7298877.<br>
        [8]    P. Ihantola et al., “Educational Data Mining and Learning Analytics in Programming : Literature Review and Case Studies,” ITiCSE WGR’16, 2015, doi: 10.1145/2858796.2858798.<br>
        [9]    “The Incredible Growth of Python | Stack Overflow,” Stack Overflow Blog, Sep. 06, 2017. https://stackoverflow.blog/2017/09/06/incredible-growth-python/ (accessed Aug. 28, 2020).<br>
        [10]    “Stack Overflow Developer Survey 2018,” Stack Overflow. https://insights.stackoverflow.com/survey/2018/?utm_source=so-owned&utm_medium=social&utm_campaign=dev-survey-2018&utm_content=social-share (accessed Aug. 28, 2020).<br>
        [11]    R. Mason and Simon, “Introductory Programming Courses in Australasia in 2016,” in Proceedings of the Nineteenth Australasian Computing Education Conference, Geelong, VIC, Australia, Jan. 2017, pp. 81–89, doi: 10.1145/3013499.3013512.<br>
        [12]    A. Luxton-Reilly et al., “Introductory programming: a systematic literature review,” in Proceedings Companion of the 23rd Annual ACM Conference on Innovation and Technology in Computer Science Education, Larnaca, Cyprus, Jul. 2018, pp. 55–106, doi: 10.1145/3293881.3295779.<br>
        </p>
        <h3>Support</h3><br>
        ${logos}`
    }
    else {
        var title = "Sobre a pesquisa"
        var content = `<p class="research">É importante entender os motivos por que alguns alunos são mais bem-sucedidos do que outros ao fazer um curso, para que possamos <span class="highlight">aprimorar os métodos de ensino</span> ao identificar as necessidades dos alunos e <span class="highlight">oferecer uma educação personalizada</span>. Um ambiente de aprendizagem inteligente é aquele que provê visualizações, simulações e inferências aos alunos e educadores a partir de dados coletados dinamicamente [1]. Sabe-se que a adoção de um ambiente de aprendizagem inteligente em salas de aula e em ambientes de auto-aprendizagem ajuda a <span class="highlight">motivar os alunos [2]-[5], melhorar a aprendizagem, diminuir os casos de abandono e a reprovação [2], [6]-[8], enquanto aumenta a autoconfiança dos alunos, especialmente em estudantes do sexo feminino [6].</span>
            </p>
            <p class="research">Além disso, o Python é uma linguagem de propósito geral, o que significa que pode ser usada em uma grande variedade de projetos. Isso é ótimo para estimular os alunos, pois eles podem trabalhar em projetos com os quais realmente se identificam. Python também possui uma interface amigável e, nos últimos sete anos, tem sido a linguagem de programação com maior crescimento em termos de adoção [9],<span class="highlight"> estando correlacionada com carreiras em alta, como DevOps e Cientista de Dados [10]</span>. De acordo com a revisão de 2015 [8],apenas 11&#37; dos artigos de Mineração de Dados Educacionais e <i>Learning Analytics</i> sobre cursos de programação relataram o uso de Python como a linguagem utilizada no curso.  No entanto, isso está mudando. Uma revisão de 2017 sobre os cursos de Introdução à Programação nas universidades da Australásia [11] relatou uma mudança de Java para Python nos últimos anos enquanto a revisão de 2018 [12] já apresentou um número maior de artigos usando Python como a linguagem principal do curso. Ainda assim, embora já tenhamos diferentes ferramentas para apoiar a aprendizagem online, ainda é difícil encontrar bancos de dados abertos contendo respostas e submissões de alunos para problemas em Python e outras informações importantes para se obter uma melhor percepção do conhecimento dos alunos.</p>
            <p class="research">As condições apresentadas motivam nossos principais objetivos: o desenvolvimento, a implantação e o uso de sistemas inteligentes online em aulas de Introdução à Programação usando a linguagem Python como uma forma de <span class="highlight">descobrir as dificuldades dos alunos, compreender seus conhecimentos e processos cognitivos de aprendizado e fornecer feedback para mantê-los envolvidos e engajados.</span>
            </p>
            Se interessou? Leia o
            <a class="highlight" target="_blank"
            href="https://drive.google.com/file/d/1SqqBEAIjiOaGY3Ajdp9tPmsw7Dc-N8Ly/view">
            nosso artigo</a>.</div>
            <p>Referências:<br>
        [1]    P. Brusilovsky et al., “Increasing Adoption of Smart Learning Content for Computer Science Education,” 2014, doi: 10.1145/2713609.2713611.<br>
        [2]    L. Benotti, M. J. Gomez, F. Aloi, and F. Bulgarelli, “The effect of a web-based coding tool with automatic feedback on students’ performance and perceptions,” SIGCSE 2018 - Proceedings of the 49th ACM Technical Symposium on Computer Science Education. 2018.<br>
        [3]    I. Jivet, M. Scheffel, M. Specht, and H. Drachsler, “License to evaluate: Preparing learning analytics dashboards for educational practice,” ACM International Conference Proceeding Series. 2018.<br>
        [4]    A. Latham, K. Crockett, D. McLean, and B. Edmonds, “A conversational intelligent tutoring system to automatically predict learning styles,” Computers and Education, vol. 59, no. 1, pp. 95–109, 2012, doi: 10.1016/j.compedu.2011.11.001.<br>
        [5]    R. Lobb and J. Harlow, “Coderunner: A tool for assessing computer programming skills,” ACM Inroads, 2016, doi: 10.1145/2810041.<br>
        [6]    A. N. Kumar, “The effect of using problem-solving software tutors on the self-confidence of female students,” ACM SIGCSE Bulletin, 2008, doi: 10.1145/1352322.1352309.<br>
        [7]    E. Johns, O. M. Aodha, and G. J. Brostow, “Becoming the expert - Interactive multi-class machine teaching,” in Proceedings of the IEEE Computer Society Conference on Computer Vision and Pattern Recognition, 2015, vol. 07-12-June, pp. 2616–2624, doi: 10.1109/CVPR.2015.7298877.<br>
        [8]    P. Ihantola et al., “Educational Data Mining and Learning Analytics in Programming : Literature Review and Case Studies,” ITiCSE WGR’16, 2015, doi: 10.1145/2858796.2858798.<br>
        [9]    “The Incredible Growth of Python | Stack Overflow,” Stack Overflow Blog, Sep. 06, 2017. https://stackoverflow.blog/2017/09/06/incredible-growth-python/ (accessed Aug. 28, 2020).<br>
        [10]    “Stack Overflow Developer Survey 2018,” Stack Overflow. https://insights.stackoverflow.com/survey/2018/?utm_source=so-owned&utm_medium=social&utm_campaign=dev-survey-2018&utm_content=social-share (accessed Aug. 28, 2020).<br>
        [11]    R. Mason and Simon, “Introductory Programming Courses in Australasia in 2016,” in Proceedings of the Nineteenth Australasian Computing Education Conference, Geelong, VIC, Australia, Jan. 2017, pp. 81–89, doi: 10.1145/3013499.3013512.<br>
        [12]    A. Luxton-Reilly et al., “Introductory programming: a systematic literature review,” in Proceedings Companion of the 23rd Annual ACM Conference on Innovation and Technology in Computer Science Education, Larnaca, Cyprus, Jul. 2018, pp. 55–106, doi: 10.1145/3293881.3295779.<br>
        </p>
        <h3>Apoio</h3><br>
        ${logos}`
    }

	showBox()
	$('.bg2 .card h3').append(title);
	$('.bg2 .card div').append(content);
};


function showTutorials(language) {
  if (language == "en") {
      var title = "Tutorials"
      var content = `<div class="tutorials">
      <div><h3>How to register?</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/5GSyIPOux4I" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div><div>
      <h3>How to answer a problem?</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/T5VY5eJvAlc" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div><div><h3>Tricks to study</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/zbt71gP0EDk" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div></div>`
    }
    else {
      var title = "Tutoriais"
      var content = `<div class="tutorials">
      <div><h3>Como se cadastrar?</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/5GSyIPOux4I" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div><div>
      <h3>Como responder um exercício?</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/T5VY5eJvAlc" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div><div><h3>Truques para estudar</h3>
      <iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/zbt71gP0EDk" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div></div>`
    }

  showBox()
  $('.bg2 .card h3').append(title);
  $('.bg2 .card div').append(content);
};