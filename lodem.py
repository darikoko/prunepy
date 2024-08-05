# for note in pizza
pizzas = [{"taste":"cheese"}, {"taste":"chorizo"}]

inside_loop_text = "pizza['taste']"



text = "pizza in pizzas"
splitted_for = text.split(" in ")
list_element = eval("pizzas")

for i in list_element:
    print(inside_loop_text[0])
    ja = eval(inside_loop_text,{},{splitted_for[0]:i})
    print(ja)

# je veux pouvoir utiliser le nom defini dans la boucle comme variable d'iteration