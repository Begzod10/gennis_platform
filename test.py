# -*- coding: utf-8 -*-
import requests

questions_and_answers =[

    {
        "index": 10,
        "question": "Finden Sie das Antonym zum Wort “kariert“",
        "answers": [
            {"text": "/gestreift/", "is_correct": 'false'},
            {"text": "/einfarbig/", "is_correct": 'true'},
            {"text": "/elegant/", "is_correct": 'false'},
            {"text": "/weit/", "is_correct": 'false'}
        ]
    },
    {
        "index": 11,
        "question": "Welche Adjektivendung passt? A: Die .... Wohnung gefällt mir gut. Sie ist aber auch teuer. B: Stimmt. Und ich fühle mich auch in einer ... Wohnung wohl.",
        "answers": [
            {"text": "/größere ... kleineren/", "is_correct": 'true'},
            {"text": "/größeren ... kleinere/", "is_correct": 'false'},
            {"text": "/größer ... kleiner/", "is_correct": 'false'},
            {"text": "/größeren ... kleineren/", "is_correct": 'false'}
        ]
    },
    {
        "index": 12,
        "question": "Ergänze die fehlenden Präpositionen und Artikel: Ich wohne in einem hellen Apartment mit vielen Fenstern ... ... man auf die Berge blicken kann.",
        "answers": [
            {"text": "/durch die/", "is_correct": 'true'},
            {"text": "/durch dem/", "is_correct": 'false'},
            {"text": "/vor dem/", "is_correct": 'false'},
            {"text": "/seit den/", "is_correct": 'false'}
        ]
    },
    {
        "index": 13,
        "question": "Welche Adjektivendung passt? Wenn mir eine Arbeit großen Spaß macht bin ich auch mit ... Gehalt zufrieden.",
        "answers": [
            {"text": "/einem niedrigeren/", "is_correct": 'true'},
            {"text": "/ein niedrigeres/", "is_correct": 'false'},
            {"text": "/einen niedrigerem/", "is_correct": 'false'},
            {"text": "/einem niedrigerem/", "is_correct": 'false'}
        ]
    },
    {
        "index": 14,
        "question": "Welches Verb passt? A: Hallo Heike du siehst heute aber nicht gut aus. B: Nein, ich komme gerade ... Arzt. Ich soll gleich wieder ... Bett gehen.",
        "answers": [
            {"text": "/vom ... ins/", "is_correct": 'true'},
            {"text": "/beim ... in/", "is_correct": 'false'},
            {"text": "/von den ... ins/", "is_correct": 'false'},
            {"text": "/vom ... im/", "is_correct": 'false'}
        ]
    },
    {
        "index": 15,
        "question": "Was passt? In einem Monat ist unsere Hochzeit. ... freue ich mich sehr!",
        "answers": [
            {"text": "/Darauf/", "is_correct": 'true'},
            {"text": "/Worauf/", "is_correct": 'false'},
            {"text": "/Dafür/", "is_correct": 'false'},
            {"text": "/Daran/", "is_correct": 'false'}
        ]
    },
    {
        "index": 16,
        "question": "Welche Präposition passt? Wir fahren oft ... ... Schweiz. Deshalb kann ich gut Deutsch.",
        "answers": [
            {"text": "/in die/", "is_correct": 'true'},
            {"text": "/nach/", "is_correct": 'false'},
            {"text": "/in den/", "is_correct": 'false'},
            {"text": "/in das/", "is_correct": 'false'}
        ]
    },
    {
        "index": 17,
        "question": "Welches Verb passt? A: Die Rechnung bitte. B: Gern zahlen Sie ... oder getrennt? A: Getrennt. B: Ein Kaffee das ... bei Ihnen 280 Euro bitte. A: Hier bitte stimmt so.",
        "answers": [
            {"text": "/zusammen ... macht/", "is_correct": 'true'},
            {"text": "/miteinander ... sind/", "is_correct": 'false'},
            {"text": "/allein ... macht/", "is_correct": 'false'},
            {"text": "/zusammen ... stimmt/", "is_correct": 'false'}
        ]
    },
    {
        "index": 18,
        "question": "Ergänzen Sie Relativpronomen: Das ist mein Freund ... Foto dir so gut gefallen hat.",
        "answers": [
            {"text": "/dessen/", "is_correct": 'true'},
            {"text": "/deren/", "is_correct": 'false'},
            {"text": "/dem/", "is_correct": 'false'},
            {"text": "/den/", "is_correct": 'false'}
        ]
    },
    {
        "index": 19,
        "question": "Ergänzen Sie den Satz? Du kannst nicht schlafen ... .",
        "answers": [
            {"text": "/weil du um 22 Uhr Kaffee getrunken hast/", "is_correct": 'true'},
            {"text": "/deshalb du um 22 Uhr Kaffee getrunken hast/", "is_correct": 'false'},
            {"text": "/deshalb hast du um 22 Uhr Kaffee getrunken/", "is_correct": 'false'},
            {"text": "/weil du hast getrunken um 22 Uhr Kaffee/", "is_correct": 'false'}
        ]
    },
    {
        "index": 20,
        "question": "Was passt? Im Fernsehen kommt ein Film ... ... ich Lust habe. Was meinst du?",
        "answers": [
            {"text": "/auf den/", "is_correct": 'true'},
            {"text": "/damit/", "is_correct": 'false'},
            {"text": "/auf der/", "is_correct": 'false'},
            {"text": "/der/", "is_correct": 'false'}
        ]
    },
    {
        "index": 21,
        "question": "Ergänzen Sie den Satz. Sie gehen fast jeden Sonntag ins Museum? Dann empfehle ich Ihnen ...",
        "answers": [
            {"text": "/eine Jahreskarte zu kaufen/", "is_correct": 'true'},
            {"text": "/kaufen Sie eine Jahreskarte/", "is_correct": 'false'},
            {"text": "/eine Jahreskarte kaufen/", "is_correct": 'false'},
            {"text": "/Sie kaufen eine Jahreskarte/", "is_correct": 'false'}
        ]
    },
    {
        "index": 22,
        "question": "Ergänzen Sie die Relativpronomen. Das sind die Kunden ... ich geholfen habe.",
        "answers": [
            {"text": "/denen/", "is_correct": 'true'},
            {"text": "/die/", "is_correct": 'false'},
            {"text": "/der/", "is_correct": 'false'},
            {"text": "/dem/", "is_correct": 'false'}
        ]
    },
    {
        "index": 23,
        "question": "Ergänzen Sie den Satz? Dr. Schröder ist schon 68 Jahre alt",
        "answers": [
            {"text": "/trotzdem arbeitet er noch als Arzt/", "is_correct": 'true'},
            {"text": "/obwohl arbeitet er noch als Arzt/", "is_correct": 'false'},
            {"text": "/obwohl er arbeitet noch als Arzt/", "is_correct": 'false'},
            {"text": "/trotzdem er noch als Arzt arbeitet/", "is_correct": 'false'}
        ]
    },
    {
        "index": 24,
        "question": "Welches Verb passt? ... ich bloß nicht abgeschrieben! Jetzt habe ich schlechte Note!",
        "answers": [
            {"text": "/Hätte/", "is_correct": 'true'},
            {"text": "/Würde/", "is_correct": 'false'},
            {"text": "/Wäre/", "is_correct": 'false'},
            {"text": "/Habe/", "is_correct": 'false'}
        ]
    },
    {
        "index": 25,
        "question": "Welche Konjunktion passt? Ich muss meine Aussprache verbessern. Nächste Woche soll ich ... mit einem deutschen Kunden telefonieren.",
        "answers": [
            {"text": "/nämlich/", "is_correct": 'true'},
            {"text": "/deshalb/", "is_correct": 'false'},
            {"text": "/darum/", "is_correct": 'false'},
            {"text": "/wegen/", "is_correct": 'false'}
        ]
    },
    {
        "index": 26,
        "question": "Welche Konjunktion passt? In meinem Traumjob möchte ich nicht nur viel Geld verdienen … zehn Wochen Urlaub haben.",
        "answers": [
            {"text": "/sondern auch/", "is_correct": 'true'},
            {"text": "/sowohl ... als auch/", "is_correct": 'false'},
            {"text": "/aber/", "is_correct": 'false'},
            {"text": "/sondern nur/", "is_correct": 'false'}
        ]
    },
    {
        "index": 27,
        "question": "Welche Konjunktion passt? Das Fest war nicht schön. ... die Kinder ... die Erwachsenen hatten Spaß.",
        "answers": [
            {"text": "/weder ... noch/", "is_correct": 'true'},
            {"text": "/sowohl ... als auch/", "is_correct": 'false'},
            {"text": "/entweder ... oder/", "is_correct": 'false'},
            {"text": "/zwar ... noch/", "is_correct": 'false'}
        ]
    },
    {
        "index": 28,
        "question": "Welche Verbform passt? Die Bühne ... drei Tage vor dem Festival fertig ... .",
        "answers": [
            {"text": "/muss ... aufgebaut sein/", "is_correct": 'true'},
            {"text": "/müsst ... aufgebaut sein/", "is_correct": 'false'},
            {"text": "/müssen ... aufbauen/", "is_correct": 'false'},
            {"text": "/muss ... aufgebaut haben/", "is_correct": 'false'}
        ]
    },
    {
        "index": 29,
        "question": "Finde den richtigen Spruch: Zu Ostern wünscht man sich ...",
        "answers": [
            {"text": "/Fröhliche Ostern!/", "is_correct": 'true'},
            {"text": "/Fröhliche Weihnachten!/", "is_correct": 'false'},
            {"text": "/Viel Erfolg!/", "is_correct": 'false'},
            {"text": "/Guten Appetit!/", "is_correct": 'false'}
        ]
    },
    {
        "index": 30,
        "question": "Bringen Sie die Sätze in die richtige Reihenfolge. 1) - Ja das geht bei mir. 2) - Gute Idee. Das machen wir. 3) - Was machen wir am Wochenende? Hast du eine Idee? 4) - Also dann bis Sonntag. 5) - Wie wäre es am Sonntag um zehn? 6) - Wir könnten einen Ausflug machen. 7) - Wann sollen wir uns treffen?",
        "answers": [
            {"text": "/3627514/", "is_correct": 'true'},
            {"text": "/4571362/", "is_correct": 'false'},
            {"text": "/2461357/", "is_correct": 'false'},
            {"text": "/7531246/", "is_correct": 'false'}
        ]
    },
    {
        "index": 31,
        "question": "Was passt? Sie möchten wirklich fünf Katzen in einer Wohnung halten? Ich rate Ihnen noch einmal ... .",
        "answers": [
            {"text": "/nachzudenken/", "is_correct": 'true'},
            {"text": "/zu denken nach/", "is_correct": 'false'},
            {"text": "/nach zu denken/", "is_correct": 'false'},
            {"text": "/nachdenken/", "is_correct": 'false'}
        ]
    },
    {
        "index": 32,
        "question": "Welche Städte gehören zur Bundesrepublik Deutschland? 1. Straßburg 2. Würzburg 3. Eichstadt 4. Nizza 5. Dresden",
        "answers": [
            {"text": "/235/", "is_correct": 'true'},
            {"text": "/135/", "is_correct": 'false'},
            {"text": "/342/", "is_correct": 'false'},
            {"text": "/234/", "is_correct": 'false'}
        ]
    },
    {
        "index": 33,
        "question": "Bringen Sie die Sätze in die richtige Reihenfolge. 1) - Schade das geht leider nicht. Meine Mutter kommt zu Besuch. Aber wie wäre es in zwei Wochen? 2) - Das ist ja toll! Wir haben schon lange nicht mehr zusammen gefrühstückt. 3) - Hallo Susi. Du ich würde dich gern zum Frühstück einladen. 4) - Da kann ich leider nicht. Da bin ich bei Freunden in Dresden. 5) - Hast du am Sonntagmorgen Zeit? 6) - Na dann vielleicht ein anderes Mal. Ich rufe dich nächste Woche nochmal an.",
        "answers": [
            {"text": "/325146/", "is_correct": 'true'},
            {"text": "/245613/", "is_correct": 'false'},
            {"text": "/135246/", "is_correct": 'false'},
            {"text": "/642531/", "is_correct": 'false'}
        ]
    },
    {
        "index": 34,
        "question": "Bringen Sie die Sätze in die richtige Reihenfolge. 1) - Schade das geht leider nicht. Meine Mutter kommt zu Besuch. Aber wie wäre es in zwei Wochen? 2) - Das ist ja toll! Wir haben schon lange nicht mehr zusammen gefrühstückt. 3) - Hallo Susi. Du ich würde dich gern zum Frühstück einladen. 4) - Da kann ich leider nicht. Da bin ich bei Freunden in Dresden. 5) - Hast du am Sonntagmorgen Zeit? 6) - Na dann vielleicht ein anderes Mal. Ich rufe dich nächste Woche nochmal an.",
        "answers": [
            {"text": "/325146/", "is_correct": "true"},
            {"text": "/245613/", "is_correct": 'false'},
            {"text": "/135246/", "is_correct": "false"},
            {"text": "/642531/", "is_correct": "false"}
        ]
    }
]

kasb_standart = [
    {
        "index": 0,
        "question": "В каких случаях можно адаптировать (вносить изменения в) учебные планы?",
        "answers": [
            {"text": "С целью учёта потребностей и интересов учащихся", "is_correct": 'true'},
            {"text": "В соответствии с требованиями родителей и потребностями учащихся", "is_correct": 'false'},
            {"text": "По предложению администрации и методического объединения", "is_correct": 'false'},
            {"text": "По приказу вышестоящей организации и администрации школы", "is_correct": 'false'}
        ]
    },
    {
        "index": 1,
        "question": "Чему должны соответствовать формы и методы планируемого урока?",
        "answers": [
            {"text": "Целям урока, возрастным особенностям и успеваемости учащихся", "is_correct": 'true'},
            {"text": "Организации и контролю коллективной и проектной работы учащихся", "is_correct": 'false'},
            {"text": "К различным образовательным процессам, а также принципам работы с одаренными детьми",
             "is_correct": 'false'},
            {"text": "Принципам общения с детьми, признания их ценности", "is_correct": 'false'}
        ]
    },
    {
        "index": 2,
        "question": "В какие трудовые функции профессиональной компетенции учителя входит “Рациональное планирование урочного времени, цели, формы и метода урока”?",
        "answers": [
            {"text": "Планирование учебного процесса", "is_correct": 'true'},
            {"text": "Организация воспитательной деятельности", "is_correct": 'false'},
            {"text": "Самосовершенствование и профессиональное развитие", "is_correct": 'false'},
            {"text": "Обеспечение эффективного обучения", "is_correct": 'false'}
        ]
    },
    {
        "index": 3,
        "question": "Какова цель использования наглядных и раздаточных материалов?",
        "answers": [
            {"text": "Обеспечение эффективности образования", "is_correct": 'true'},
            {"text": "Обеспечение дифференцированного подхода", "is_correct": 'false'},
            {"text": "Саморазвитие и профессиональный рост", "is_correct": 'false'},
            {"text": "Выставление оценок и предоставление обратной связи", "is_correct": 'false'}
        ]
    },
    {
        "index": 4,
        "question": "Во время урока учитель дал возможность высказаться большинству учащихся. Не отвергая неправильные суждения, он попытался с помощью наводящих вопросов объяснить новую тему. С какой целью был использован данный метод?",
        "answers": [
            {"text": "Для того чтобы в ходе урока дать каждому ученику возможность выразить свои идеи и взгляды",
             "is_correct": 'true'},
            {"text": "С целью правильного применения возрастной педагогики и психологии методов работы с детьми",
             "is_correct": 'false'},
            {"text": "С целью дифференцированного подхода и объективной оценки знаний учащихся", "is_correct": 'false'},
            {"text": "Для того чтобы правильно и эффективно организовать коллективную и проектную работу учащихся",
             "is_correct": 'false'}
        ]
    }
]

kasb = [
    {
        "index": 0,
        "question": "Ученику для выполнения практического задания была представлена конкретная задача и определены условия её решения. Ученик спланировал свои действия относительно поставленной перед ним задачи. К какому виду деятельности относится эта способность?",
        "answers": [
            {"text": "Регулятивная (целеполагание, планирование, саморегуляция, преодоление препятствий)",
             "is_correct": 'true'},
            {"text": "Коммуникативная (навыки межличностного отношения, работа и взаимодействие с другими)",
             "is_correct": 'false'},
            {"text": "Когнитивная (усвоение новой информации, понимание окружающего нас мира и взаимодействие с ним)",
             "is_correct": 'false'},
            {"text": "Конструктивная (создание модели, интерпретирование и использование графической информации)",
             "is_correct": 'false'}
        ]
    },
    {
        "index": 1,
        "question": "Учитель хочет повысить уровень самостоятельной деятельности ученика. Какой для этого должна быть последовательность методов обучения?",
        "answers": [
            {
                "text": "2134 (Сбор информации – рецептивный метод, Репродуктивный метод, Метод проблемного обучения, Метод исследования)",
                "is_correct": 'true'},
            {"text": "1423", "is_correct": 'false'},
            {"text": "2143", "is_correct": 'false'},
            {"text": "3124", "is_correct": 'false'}
        ]
    },
    {
        "index": 2,
        "question": "Планируется проведение мониторинга по определению качества образования в школе. Выберите варианты которые правильно обозначают его функции:",
        "answers": [
            {
                "text": "1235 (Сбор информации, анализ и оценка качества образования; Контроль выполнения социального заказа; Мотивационное воздействие; Разработка рекомендаций по корректировкам)",
                "is_correct": 'true'},
            {"text": "245", "is_correct": 'false'},
            {"text": "125", "is_correct": 'false'},
            {"text": "2345", "is_correct": 'false'}
        ]
    },
    {
        "index": 3,
        "question": "Учитель разделил учащихся на несколько групп и предложил им темы проектных работ по различным направлениям. Выберите варианты которые относятся к виду экологического проекта:",
        "answers": [
            {
                "text": "12 (Организация работ по сортировке мусора в школе; Создание ветреного генератора для освещения спортивной площадки)",
                "is_correct": 'true'},
            {"text": "14", "is_correct": 'false'},
            {"text": "23", "is_correct": 'false'},
            {"text": "24", "is_correct": 'false'}
        ]
    },
    {
        "index": 4,
        "question": "Учитель привел факты и суждения по новой теме и задал учащимся вопросы по ним. Какой навык формируется у ученика таким образом?",
        "answers": [
            {"text": "Знание", "is_correct": 'true'},
            {"text": "Применение", "is_correct": 'false'},
            {"text": "Анализ", "is_correct": 'false'},
            {"text": "Рассуждение", "is_correct": 'false'}
        ]
    },
    {
        "index": 5,
        "question": "Учитель предоставил учащимся готовые знания по конкретной теме, а затем организовал работу по закреплению, обобщению, систематизации и контролю. К какому виду обучения относится данная технология?",
        "answers": [
            {"text": "Репродуктивное обучение", "is_correct": 'true'},
            {"text": "Проблемное обучение", "is_correct": 'false'},
            {"text": "Личностно-ориентированное обучение", "is_correct": 'false'},
            {"text": "Дифференцированное обучение", "is_correct": 'false'}
        ]
    },
    {
        "index": 6,
        "question": "Учитель дал ученику задание для самостоятельной работы. Чтобы выполнить задание, ученику был предоставлен список литературы. Также ему было предложено дополнить свою работу собственными выводами. Каким видом обучения воспользовался учитель для развития творческих способностей ученика?",
        "answers": [
            {"text": "Личностно-ориентированное обучение", "is_correct": 'true'},
            {"text": "Проблемное обучение", "is_correct": 'false'},
            {"text": "Социализированное обучение", "is_correct": 'false'},
            {"text": "Внеклассное обучение", "is_correct": 'false'}
        ]
    },
    {
        "index": 7,
        "question": "Преподаватель работал над авторской программой и концепцией развития школы. Каким видом деятельности учителя является такой процесс?",
        "answers": [
            {"text": "Инновационная деятельность учителя", "is_correct": 'true'},
            {"text": "Общественная деятельность учителя", "is_correct": 'false'},
            {"text": "Внешкольная деятельность учителя", "is_correct": 'false'},
            {"text": "Дополнительная деятельность учителя", "is_correct": 'false'}
        ]
    },
    {
        "index": 8,
        "question": "Молодой специалист объяснил на уроке новую тему. Затем ученики обратились к нему с вопросом: 'А для чего нам все это нужно? Мы не хотим этому учиться'. Как вы думаете, какие компоненты образовательного процесса учитель не реализовал в полной мере?",
        "answers": [
            {"text": "12 (Цель урока, содержание)", "is_correct": 'true'},
            {"text": "23 (Содержание, контроль)", "is_correct": 'false'},
            {"text": "14 (Цель урока, оценка)", "is_correct": 'false'},
            {"text": "24 (Контроль, оценка)", "is_correct": 'false'}
        ]
    },
    {
        "index": 9,
        "question": "Учитель во время урока дал возможность высказаться большинству учащихся. Не отвергая неправильные суждения, он попытался с помощью наводящих вопросов объяснить новую тему. С какой целью был использован данный метод?",
        "answers": [
            {"text": "Для того чтобы в ходе урока дать каждому ученику возможность выразить свои идеи и взгляды",
             "is_correct": 'true'},
            {"text": "С целью правильного применения возрастной педагогики и психологии методов работы с детьми",
             "is_correct": 'false'},
            {"text": "С целью дифференцированного подхода и объективной оценки знаний учащихся", "is_correct": 'false'},
            {"text": "Для того чтобы правильно и эффективно организовать коллективную и проектную работу учащихся",
             "is_correct": 'false'}
        ]
    }
]


def send_question(test_id, question_text):
    url = 'https://teachers-ru.avotra.ru/Question/questions/'
    headers = {
        'accept': 'application/json',
        'x-csrftoken': '9K7bqjEv9ejwYHB9vJqodd7c421nwWWd49XRY4WcpmRcaDeAXYAH6sCC3eQZRBn8',
    }

    data = {
        'test': test_id,
        'question': question_text,
    }

    response = requests.post(url, headers=headers, data=data)
    return response


def send_answer(test_id, question_id, answer_text, status):
    url = 'https://teachers-ru.avotra.ru/Answers/answers/'
    headers = {
        'accept': 'application/json',
        'x-csrftoken': 't5HLJrMxMTZZktaxxfllaKqfmRh6WGlMouxrhc4e21xFwpNYZuvE3ZVFl36IhlMH',
    }

    data = {
        'test': test_id,
        'question': question_id,
        'answer': answer_text,
        'status': str(status).lower()
    }

    response = requests.post(url, headers=headers, data=data)
    return response


for q in questions_and_answers:
    question_response = send_question(57, q["question"])
    if question_response.status_code == 201:
        print(f"Question '{q['index']}' sent successfully.")
        question_id = question_response.json().get("id")

        if question_id is not None:
            for answer in q["answers"]:
                answer_response = send_answer(57, question_id, answer["text"], answer["is_correct"])
                if answer_response.status_code == 201:
                    print(f"Answer '{answer['text']}' for question '{question_id}' sent successfully.")
                else:
                    print(
                        f"Failed to send answer '{answer['text']}' for question '{q['question']}'. Status code: {answer_response.status_code}")
        else:
            print(f"Failed to retrieve question ID for question '{q['question']}'.")
    else:
        print(
            f"Failed to send question '{q['question']}'. Status code: {question_response.status_code}, {question_response.text}")

for q in kasb_standart:
    question_response = send_question(57, q["question"])
    if question_response.status_code == 201:
        print(f"Question '{q['index']}' sent successfully.")
        question_id = question_response.json().get("id")

        if question_id is not None:
            for answer in q["answers"]:
                answer_response = send_answer(57, question_id, answer["text"], answer["is_correct"])
                if answer_response.status_code == 201:
                    print(f"Answer '{answer['text']}' for question '{question_id}' sent successfully.")
                else:
                    print(
                        f"Failed to send answer '{answer['text']}' for question '{q['question']}'. Status code: {answer_response.status_code}")
        else:
            print(f"Failed to retrieve question ID for question '{q['question']}'.")
    else:
        print(
            f"Failed to send question '{q['question']}'. Status code: {question_response.status_code}, {question_response.text}")

for q in kasb:
    question_response = send_question(57, q["question"])
    if question_response.status_code == 201:
        print(f"Question '{q['index']}' sent successfully.")
        question_id = question_response.json().get("id")

        if question_id is not None:
            for answer in q["answers"]:
                answer_response = send_answer(57, question_id, answer["text"], answer["is_correct"])
                if answer_response.status_code == 201:
                    print(f"Answer '{answer['text']}' for question '{question_id}' sent successfully.")
                else:
                    print(
                        f"Failed to send answer '{answer['text']}' for question '{q['question']}'. Status code: {answer_response.status_code}")
        else:
            print(f"Failed to retrieve question ID for question '{q['question']}'.")
    else:
        print(
            f"Failed to send question '{q['question']}'. Status code: {question_response.status_code}, {question_response.text}")
